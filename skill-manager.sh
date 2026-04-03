#!/usr/bin/env bash
# Codex Skills Manager — CLI tool for installing/managing shared Codex skills
# Requires: bash 4.0+
# Optional: jq (recommended for reliable JSON parsing)

set -uo pipefail

if (( BASH_VERSINFO[0] < 4 )); then
    cat <<'EOF'
Error: skill-manager.sh requires Bash 4 or newer.

macOS ships /bin/bash 3.2 by default, which is not supported by this script.
Install a newer Bash and rerun the manager with that binary after confirming:
  bash --version
EOF
    exit 1
fi

# ─── Resolve skill-base directory (where this script lives) ───
SKILL_BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE_DIR="${SKILL_BASE_DIR}/skill-base"

# ─── Resolve target project skills directory ───
PROJECT_DIR="$(pwd)"
SKILLS_TARGET_DIR="${PROJECT_DIR}/.agents/skills"

# ─── Colors ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

# ─── JSON parser setup (auto-detect jq) ───
if command -v jq &>/dev/null; then
    parse_json() {
        local key="$1" file="$2"
        jq -r ".$key // empty" "$file" 2>/dev/null
    }
else
    echo -e "${YELLOW}Warning: jq not found, using basic parser (recommend: brew install jq / apt install jq)${NC}"
    parse_json() {
        local key="$1" file="$2"
        grep -o "\"${key}\": *\"[^\"]*\"" "$file" 2>/dev/null | head -1 | sed 's/.*": *"//;s/"$//'
    }
fi

# ─── Helpers ───

AVAILABLE_SKILLS=()
INVALID_SOURCE_SKILLS=()
INVALID_SOURCE_MESSAGES=()
INSTALLED_SKILLS=()
INVALID_INSTALLED_SKILLS=()
INVALID_INSTALLED_MESSAGES=()
UNKNOWN_INSTALLED_SKILLS=()
UNKNOWN_INSTALLED_MESSAGES=()

print_header() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${BOLD}            Codex Skills Manager               ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}╠═══════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC}                                               ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  1) Install / Update skills                   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  2) Remove installed skills                   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  3) List installed skills                     ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}  4) Exit                                      ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                                               ${CYAN}║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${DIM}  Skill base   : ${SKILLS_SOURCE_DIR}${NC}"
    echo -e "${DIM}  Project      : ${PROJECT_DIR}${NC}"
    echo -e "${DIM}  Install path : ${SKILLS_TARGET_DIR}${NC}"
    echo ""
}

trim_value() {
    local value="$1"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    printf '%s' "$value"
}

get_frontmatter_name() {
    local file="$1"
    [[ -f "$file" ]] || return 0

    awk '
NR == 1 && $0 == "---" { in_fm = 1; next }
in_fm && $0 == "---" { exit }
in_fm && $1 == "name:" {
    sub(/^name:[[:space:]]*/, "", $0)
    gsub(/^["'"'"']|["'"'"']$/, "", $0)
    print
    exit
}
' "$file"
}

validate_skill_dir() {
    local skill_dir="$1"
    local expected_name
    expected_name="$(basename "$skill_dir")"

    local errors=()
    local skill_md="${skill_dir}/SKILL.md"
    local metadata="${skill_dir}/metadata.json"

    [[ -d "$skill_dir" ]] || errors+=("missing skill directory")
    [[ -f "$skill_md" ]] || errors+=("missing SKILL.md")
    [[ -f "$metadata" ]] || errors+=("missing metadata.json")

    local metadata_name=""
    local metadata_version=""
    local metadata_category=""
    local metadata_description=""
    local frontmatter_name=""

    if [[ -f "$metadata" ]]; then
        metadata_name="$(trim_value "$(parse_json "name" "$metadata")")"
        metadata_version="$(trim_value "$(parse_json "version" "$metadata")")"
        metadata_category="$(trim_value "$(parse_json "category" "$metadata")")"
        metadata_description="$(trim_value "$(parse_json "description" "$metadata")")"

        [[ -n "$metadata_name" ]] || errors+=("metadata missing name")
        [[ -n "$metadata_version" ]] || errors+=("metadata missing version")
        [[ -n "$metadata_category" ]] || errors+=("metadata missing category")
        [[ -n "$metadata_description" ]] || errors+=("metadata missing description")
    fi

    if [[ -f "$skill_md" ]]; then
        frontmatter_name="$(trim_value "$(get_frontmatter_name "$skill_md")")"
        [[ -n "$frontmatter_name" ]] || errors+=("SKILL.md frontmatter missing name")
    fi

    if [[ -n "$metadata_name" && "$metadata_name" != "$expected_name" ]]; then
        errors+=("metadata name '${metadata_name}' does not match directory '${expected_name}'")
    fi

    if [[ -n "$frontmatter_name" && "$frontmatter_name" != "$expected_name" ]]; then
        errors+=("SKILL.md frontmatter name '${frontmatter_name}' does not match directory '${expected_name}'")
    fi

    if [[ -n "$metadata_name" && -n "$frontmatter_name" && "$metadata_name" != "$frontmatter_name" ]]; then
        errors+=("metadata name '${metadata_name}' does not match SKILL.md frontmatter name '${frontmatter_name}'")
    fi

    if (( ${#errors[@]} > 0 )); then
        local joined=""
        local error
        for error in "${errors[@]}"; do
            if [[ -n "$joined" ]]; then
                joined+="; "
            fi
            joined+="$error"
        done
        printf '%s\n' "$joined"
        return 1
    fi
}

has_metadata_shape() {
    local skill_dir="$1"
    local metadata="${skill_dir}/metadata.json"
    [[ -f "$metadata" ]] || return 1

    local metadata_name=""
    local metadata_version=""
    local metadata_category=""
    local metadata_description=""

    metadata_name="$(trim_value "$(parse_json "name" "$metadata")")"
    metadata_version="$(trim_value "$(parse_json "version" "$metadata")")"
    metadata_category="$(trim_value "$(parse_json "category" "$metadata")")"
    metadata_description="$(trim_value "$(parse_json "description" "$metadata")")"

    [[ -n "$metadata_name" || -n "$metadata_version" || -n "$metadata_category" || -n "$metadata_description" ]]
}

is_available_skill() {
    local skill_name="$1"
    local skill
    for skill in "${AVAILABLE_SKILLS[@]}"; do
        [[ "$skill" == "$skill_name" ]] && return 0
    done
    return 1
}

is_installed_skill() {
    local skill_name="$1"
    local skill
    for skill in "${INSTALLED_SKILLS[@]}"; do
        [[ "$skill" == "$skill_name" ]] && return 0
    done
    return 1
}

scan_available_skills() {
    AVAILABLE_SKILLS=()
    INVALID_SOURCE_SKILLS=()
    INVALID_SOURCE_MESSAGES=()

    local dir
    for dir in "${SKILLS_SOURCE_DIR}"/*/; do
        [[ -d "$dir" ]] || continue
        local name
        local error
        name="$(basename "$dir")"
        if error="$(validate_skill_dir "$dir" 2>/dev/null)"; then
            AVAILABLE_SKILLS+=("$name")
        else
            INVALID_SOURCE_SKILLS+=("$name")
            INVALID_SOURCE_MESSAGES+=("${name}: ${error}")
        fi
    done
}

scan_installed_skills() {
    INSTALLED_SKILLS=()
    INVALID_INSTALLED_SKILLS=()
    INVALID_INSTALLED_MESSAGES=()
    UNKNOWN_INSTALLED_SKILLS=()
    UNKNOWN_INSTALLED_MESSAGES=()

    [[ -d "$SKILLS_TARGET_DIR" ]] || return

    local dir
    for dir in "${SKILLS_TARGET_DIR}"/*/; do
        [[ -d "$dir" ]] || continue
        local name
        local error
        name="$(basename "$dir")"
        if ! is_available_skill "$name"; then
            UNKNOWN_INSTALLED_SKILLS+=("$name")
            UNKNOWN_INSTALLED_MESSAGES+=("${name}: not managed by this skill-base")
        elif error="$(validate_skill_dir "$dir" 2>/dev/null)"; then
            INSTALLED_SKILLS+=("$name")
        elif has_metadata_shape "$dir"; then
            INVALID_INSTALLED_SKILLS+=("$name")
            INVALID_INSTALLED_MESSAGES+=("${name}: ${error}")
        else
            UNKNOWN_INSTALLED_SKILLS+=("$name")
            UNKNOWN_INSTALLED_MESSAGES+=("${name}: local skill or unsupported package layout")
        fi
    done
}

print_invalid_source_warnings() {
    (( ${#INVALID_SOURCE_MESSAGES[@]} > 0 )) || return

    echo ""
    echo -e "${YELLOW}Skipped invalid skill packages in skill-base:${NC}"
    local message
    for message in "${INVALID_SOURCE_MESSAGES[@]}"; do
        echo -e "  - ${message}"
    done
}

print_invalid_installed_warnings() {
    (( ${#INVALID_INSTALLED_MESSAGES[@]} > 0 )) || return

    echo ""
    echo -e "${YELLOW}Broken installed skill packages:${NC}"
    local message
    for message in "${INVALID_INSTALLED_MESSAGES[@]}"; do
        echo -e "  - ${message}"
    done
}

print_unknown_installed_notes() {
    (( ${#UNKNOWN_INSTALLED_MESSAGES[@]} > 0 )) || return

    echo ""
    echo -e "${DIM}Unmanaged local skills:${NC}"
    local message
    for message in "${UNKNOWN_INSTALLED_MESSAGES[@]}"; do
        echo -e "  - ${message}"
    done
}

get_version() {
    local skill_dir="$1"
    if [[ -f "${skill_dir}/metadata.json" ]]; then
        parse_json "version" "${skill_dir}/metadata.json"
    else
        echo "unknown"
    fi
}

get_description() {
    local skill_dir="$1"
    if [[ -f "${skill_dir}/metadata.json" ]]; then
        parse_json "description" "${skill_dir}/metadata.json"
    else
        echo ""
    fi
}

get_category() {
    local skill_dir="$1"
    if [[ -f "${skill_dir}/metadata.json" ]]; then
        local cat
        cat="$(parse_json "category" "${skill_dir}/metadata.json")"
        echo "${cat:-uncategorized}"
    else
        echo "uncategorized"
    fi
}

install_skill_dir() {
    local skill="$1"
    local source_dir="${SKILLS_SOURCE_DIR}/${skill}"
    local target_dir="${SKILLS_TARGET_DIR}/${skill}"

    rm -rf "$target_dir"
    mkdir -p "$target_dir" || return 1
    cp -R "${source_dir}/." "$target_dir/" || return 1

    [[ -f "${target_dir}/SKILL.md" ]] || return 1
    [[ -f "${target_dir}/metadata.json" ]] || return 1
}

# ─── Install / Update ───

do_install() {
    echo ""
    echo -e "${BOLD}Available skills:${NC}"

    scan_available_skills
    print_invalid_source_warnings

    if [[ ${#AVAILABLE_SKILLS[@]} -eq 0 ]]; then
        echo -e "  ${YELLOW}No valid skills found in ${SKILLS_SOURCE_DIR}${NC}"
        return
    fi

    scan_installed_skills

    declare -A skill_map
    declare -A category_skills
    local categories=()

    local skill
    for skill in "${AVAILABLE_SKILLS[@]}"; do
        local cat
        cat="$(get_category "${SKILLS_SOURCE_DIR}/${skill}")"
        category_skills[$cat]+="${skill} "
        local found=false
        for c in "${categories[@]}"; do
            [[ "$c" == "$cat" ]] && { found=true; break; }
        done
        $found || categories+=("$cat")
    done

    mapfile -t categories <<< "$(printf '%s\n' "${categories[@]}" | sort | grep -v '^uncategorized$'; printf '%s\n' "${categories[@]}" | grep '^uncategorized$' 2>/dev/null || true)"

    local i=1
    for cat in "${categories[@]}"; do
        [[ -z "$cat" ]] && continue
        echo ""
        echo -e "  ${CYAN}── ${cat} ──${NC}"
        echo ""

        read -ra cat_skills <<< "${category_skills[$cat]}"
        for skill in "${cat_skills[@]}"; do
            local src_version src_desc status_label
            src_version="$(get_version "${SKILLS_SOURCE_DIR}/${skill}")"
            src_desc="$(get_description "${SKILLS_SOURCE_DIR}/${skill}")"

            local is_installed=false
            local is_unknown=false
            local installed_version=""
            for inst in "${INSTALLED_SKILLS[@]}"; do
                if [[ "$inst" == "$skill" ]]; then
                    is_installed=true
                    installed_version="$(get_version "${SKILLS_TARGET_DIR}/${skill}")"
                    break
                fi
            done
            if ! $is_installed; then
                for inst in "${UNKNOWN_INSTALLED_SKILLS[@]}"; do
                    if [[ "$inst" == "$skill" ]]; then
                        is_unknown=true
                        break
                    fi
                done
            fi

            if $is_installed; then
                if [[ "$installed_version" == "$src_version" ]]; then
                    status_label="${GREEN}[installed v${installed_version} ✓]${NC}"
                else
                    status_label="${YELLOW}[installed v${installed_version} ↑ update]${NC}"
                fi
            elif $is_unknown; then
                status_label="${YELLOW}[unknown local package]${NC}"
            else
                status_label="${DIM}[not installed]${NC}"
            fi

            printf "  ${BOLD}[%d]${NC} %-14s ${DIM}v%-8s${NC} %-40s %b\n" \
                "$i" "$skill" "$src_version" "$src_desc" "$status_label"

            skill_map[$i]="$skill"
            ((i++))
        done
    done

    echo ""
    echo -e "Enter numbers to install/update (comma separated, or ${BOLD}'a'${NC} for all, ${BOLD}'q'${NC} to cancel):"
    read -rp "> " selection

    [[ "$selection" == "q" || -z "$selection" ]] && return

    local selected_skills=()
    if [[ "$selection" == "a" ]]; then
        selected_skills=("${AVAILABLE_SKILLS[@]}")
    else
        IFS=',' read -ra nums <<< "$selection"
        for num in "${nums[@]}"; do
            num="$(echo "$num" | tr -d ' ')"
            if [[ -n "${skill_map[$num]+x}" ]]; then
                selected_skills+=("${skill_map[$num]}")
            else
                echo -e "${RED}Invalid selection: $num${NC}"
            fi
        done
    fi

    if [[ ${#selected_skills[@]} -eq 0 ]]; then
        echo -e "${YELLOW}No skills selected.${NC}"
        return
    fi

    local has_updates=false
    local has_unknown_replacements=false
    echo ""
    echo -e "${BOLD}Will install/update:${NC}"
    for skill in "${selected_skills[@]}"; do
        local src_ver
        src_ver="$(get_version "${SKILLS_SOURCE_DIR}/${skill}")"
        if is_installed_skill "$skill"; then
            local cur_ver
            cur_ver="$(get_version "${SKILLS_TARGET_DIR}/${skill}")"
            echo -e "  • ${skill} ${DIM}v${cur_ver}${NC} → ${GREEN}v${src_ver}${NC}"
            has_updates=true
        elif [[ -d "${SKILLS_TARGET_DIR}/${skill}" ]]; then
            echo -e "  • ${skill} ${YELLOW}[unknown local package]${NC} → ${GREEN}v${src_ver}${NC}"
            has_unknown_replacements=true
        else
            echo -e "  • ${skill} ${GREEN}v${src_ver}${NC} ${DIM}(new)${NC}"
        fi
    done

    if $has_updates; then
        echo ""
        echo -e "${YELLOW}Warning:${NC} updates replace the entire skill package, not just SKILL.md."
    fi
    if $has_unknown_replacements; then
        echo ""
        echo -e "${YELLOW}Warning:${NC} installing over an unknown local package will replace that directory."
    fi

    echo ""
    read -rp "Proceed? [y/N] " confirm
    [[ "$confirm" != "y" && "$confirm" != "Y" ]] && { echo "Cancelled."; return; }

    mkdir -p "$SKILLS_TARGET_DIR" || {
        echo -e "${RED}Failed to create install path: ${SKILLS_TARGET_DIR}${NC}"
        return
    }

    local success_count=0
    local failure_count=0
    for skill in "${selected_skills[@]}"; do
        if install_skill_dir "$skill"; then
            ((success_count++))
            echo -e "  ${GREEN}✓${NC} Installed ${BOLD}${skill}${NC}"
        else
            ((failure_count++))
            echo -e "  ${RED}✗${NC} Failed to install ${BOLD}${skill}${NC}"
        fi
    done

    echo ""
    if (( success_count > 0 )); then
        echo -e "${GREEN}Done! ${success_count} skill(s) installed/updated.${NC}"
    fi
    if (( failure_count > 0 )); then
        echo -e "${RED}${failure_count} skill(s) failed to install/update.${NC}"
    fi
    echo -e "${DIM}Installed to project-local .agents/skills.${NC}"
}

# ─── Remove ───

do_remove() {
    echo ""
    echo -e "${BOLD}Installed skills:${NC}"
    echo ""

    scan_available_skills
    scan_installed_skills

    if (( ${#INSTALLED_SKILLS[@]} == 0 && ${#INVALID_INSTALLED_SKILLS[@]} == 0 )); then
        echo -e "  ${YELLOW}No skills installed in ${SKILLS_TARGET_DIR}${NC}"
        print_unknown_installed_notes
        return
    fi

    local i=1
    declare -A skill_map
    local skill
    for skill in "${INSTALLED_SKILLS[@]}"; do
        local ver
        ver="$(get_version "${SKILLS_TARGET_DIR}/${skill}")"
        printf "  ${BOLD}[%d]${NC} %-14s ${DIM}v%s${NC}\n" "$i" "$skill" "$ver"
        skill_map[$i]="$skill"
        ((i++))
    done

    for skill in "${INVALID_INSTALLED_SKILLS[@]}"; do
        printf "  ${BOLD}[%d]${NC} %-14s ${YELLOW}[broken]${NC}\n" "$i" "$skill"
        skill_map[$i]="$skill"
        ((i++))
    done

    print_invalid_installed_warnings
    print_unknown_installed_notes

    echo ""
    echo -e "Enter numbers to remove (comma separated, or ${BOLD}'q'${NC} to cancel):"
    read -rp "> " selection

    [[ "$selection" == "q" || -z "$selection" ]] && return

    local selected_skills=()
    IFS=',' read -ra nums <<< "$selection"
    for num in "${nums[@]}"; do
        num="$(echo "$num" | tr -d ' ')"
        if [[ -n "${skill_map[$num]+x}" ]]; then
            selected_skills+=("${skill_map[$num]}")
        else
            echo -e "${RED}Invalid selection: $num${NC}"
        fi
    done

    if [[ ${#selected_skills[@]} -eq 0 ]]; then
        echo -e "${YELLOW}No skills selected.${NC}"
        return
    fi

    echo ""
    echo -e "${BOLD}Will remove:${NC}"
    for skill in "${selected_skills[@]}"; do
        echo -e "  • ${RED}${skill}${NC}"
    done

    echo ""
    read -rp "Proceed? [y/N] " confirm
    [[ "$confirm" != "y" && "$confirm" != "Y" ]] && { echo "Cancelled."; return; }

    local count=0
    for skill in "${selected_skills[@]}"; do
        rm -rf "${SKILLS_TARGET_DIR:?}/${skill}"
        ((count++))
        echo -e "  ${GREEN}✓${NC} Removed ${BOLD}${skill}${NC}"
    done

    echo ""
    echo -e "${GREEN}Done! ${count} skill(s) removed.${NC}"
}

# ─── List ───

do_list() {
    echo ""
    echo -e "${BOLD}Installed skills:${NC}"

    scan_available_skills
    scan_installed_skills

    if (( ${#INSTALLED_SKILLS[@]} == 0 && ${#INVALID_INSTALLED_SKILLS[@]} == 0 )); then
        echo -e "  ${YELLOW}No skills installed in ${SKILLS_TARGET_DIR}${NC}"
        print_unknown_installed_notes
        return
    fi

    declare -A category_skills
    local categories=()

    local skill
    for skill in "${INSTALLED_SKILLS[@]}"; do
        local cat
        cat="$(get_category "${SKILLS_TARGET_DIR}/${skill}")"
        category_skills[$cat]+="${skill} "
        local found=false
        for c in "${categories[@]}"; do
            [[ "$c" == "$cat" ]] && { found=true; break; }
        done
        $found || categories+=("$cat")
    done

    mapfile -t categories <<< "$(printf '%s\n' "${categories[@]}" | sort | grep -v '^uncategorized$'; printf '%s\n' "${categories[@]}" | grep '^uncategorized$' 2>/dev/null || true)"

    for cat in "${categories[@]}"; do
        [[ -z "$cat" ]] && continue
        echo ""
        echo -e "  ${CYAN}── ${cat} ──${NC}"
        echo ""

        read -ra cat_skills <<< "${category_skills[$cat]}"
        for skill in "${cat_skills[@]}"; do
            local ver desc status_label
            ver="$(get_version "${SKILLS_TARGET_DIR}/${skill}")"
            desc="$(get_description "${SKILLS_TARGET_DIR}/${skill}")"

            if [[ -f "${SKILLS_SOURCE_DIR}/${skill}/metadata.json" ]]; then
                local src_ver
                src_ver="$(get_version "${SKILLS_SOURCE_DIR}/${skill}")"
                if [[ "$ver" == "$src_ver" ]]; then
                    status_label="${GREEN}[up to date]${NC}"
                else
                    status_label="${YELLOW}[v${src_ver} available ↑]${NC}"
                fi
            else
                status_label="${DIM}[not in skill-base]${NC}"
            fi

            printf "  %-14s ${DIM}v%-8s${NC} %-40s %b\n" \
                "$skill" "$ver" "$desc" "$status_label"
        done
    done

    print_invalid_installed_warnings
    print_unknown_installed_notes
    echo ""
}

# ─── Main loop ───

main() {
    if [[ ! -d "$SKILLS_SOURCE_DIR" ]]; then
        echo -e "${RED}Error: Skills directory not found at ${SKILLS_SOURCE_DIR}${NC}"
        echo -e "Make sure you're running the script from a valid skill-base repo."
        exit 1
    fi

    while true; do
        print_header
        read -rp "Select an option [1-4]: " choice
        case "$choice" in
            1) do_install ;;
            2) do_remove ;;
            3) do_list ;;
            4) echo -e "\n${GREEN}Bye!${NC}"; exit 0 ;;
            *) echo -e "${RED}Invalid option.${NC}" ;;
        esac

        echo ""
        read -rp "Press Enter to continue..." _
    done
}

main "$@"
