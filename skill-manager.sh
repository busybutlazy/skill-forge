#!/usr/bin/env bash
# Codex Skills Manager — CLI tool for installing/managing shared Codex skills
# Requires: bash 4.0+, diff
# Optional: jq (recommended for reliable JSON parsing)

set -uo pipefail

# ─── Resolve skill-base directory (where this script lives) ───
SKILL_BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SOURCE_DIR="${SKILL_BASE_DIR}/skill-base"

get_file_hash() {
    local file="$1"
    if command -v md5sum >/dev/null 2>&1; then
        md5sum "$file" | cut -d' ' -f1
    elif command -v md5 >/dev/null 2>&1; then
        md5 -q "$file"
    elif command -v shasum >/dev/null 2>&1; then
        shasum "$file" | cut -d' ' -f1
    else
        echo ""
    fi
}

# ─── Auto-update skill-base from remote ───
_self_hash="$(get_file_hash "${BASH_SOURCE[0]}")"
echo -e "Updating skill-base..."
git -C "$SKILL_BASE_DIR" pull --quiet 2>/dev/null || echo -e "Warning: Failed to update skill-base (offline or not a git repo), using local version."
if [[ -n "$_self_hash" && "$(get_file_hash "${BASH_SOURCE[0]}")" != "$_self_hash" ]]; then
    echo -e "Script updated, restarting..."
    exec "$0" "$@"
fi

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

get_available_skills() {
    local skills=()
    for dir in "${SKILLS_SOURCE_DIR}"/*/; do
        [[ -d "$dir" ]] || continue
        local name
        name="$(basename "$dir")"
        [[ -f "${dir}/metadata.json" && -f "${dir}/SKILL.md" ]] && skills+=("$name")
    done
    echo "${skills[@]}"
}

get_installed_skills() {
    local skills=()
    [[ -d "$SKILLS_TARGET_DIR" ]] || { echo ""; return; }
    for dir in "${SKILLS_TARGET_DIR}"/*/; do
        [[ -d "$dir" ]] || continue
        local name
        name="$(basename "$dir")"
        [[ -f "${dir}/SKILL.md" ]] && skills+=("$name")
    done
    echo "${skills[@]}"
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
    mkdir -p "$target_dir"
    cp -R "${source_dir}/." "$target_dir/"
}

# ─── Install / Update ───

do_install() {
    echo ""
    echo -e "${BOLD}Available skills:${NC}"

    local available
    read -ra available <<< "$(get_available_skills)"

    if [[ ${#available[@]} -eq 0 ]]; then
        echo -e "  ${YELLOW}No skills found in ${SKILLS_SOURCE_DIR}${NC}"
        return
    fi

    local installed
    read -ra installed <<< "$(get_installed_skills)"

    declare -A skill_map
    declare -A category_skills
    local categories=()

    for skill in "${available[@]}"; do
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
            local installed_version=""
            for inst in "${installed[@]}"; do
                if [[ "$inst" == "$skill" ]]; then
                    is_installed=true
                    installed_version="$(get_version "${SKILLS_TARGET_DIR}/${skill}")"
                    break
                fi
            done

            if $is_installed; then
                if [[ "$installed_version" == "$src_version" ]]; then
                    status_label="${GREEN}[installed v${installed_version} ✓]${NC}"
                else
                    status_label="${YELLOW}[installed v${installed_version} ↑ update]${NC}"
                fi
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
        selected_skills=("${available[@]}")
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

    echo ""
    echo -e "${BOLD}Will install/update:${NC}"
    for skill in "${selected_skills[@]}"; do
        local src_ver
        src_ver="$(get_version "${SKILLS_SOURCE_DIR}/${skill}")"
        if [[ -d "${SKILLS_TARGET_DIR}/${skill}" ]]; then
            local cur_ver
            cur_ver="$(get_version "${SKILLS_TARGET_DIR}/${skill}")"
            echo -e "  • ${skill} ${DIM}v${cur_ver}${NC} → ${GREEN}v${src_ver}${NC}"

            if [[ -f "${SKILLS_TARGET_DIR}/${skill}/SKILL.md" && -f "${SKILLS_SOURCE_DIR}/${skill}/SKILL.md" ]]; then
                local diff_output
                diff_output="$(diff --unified=1 "${SKILLS_TARGET_DIR}/${skill}/SKILL.md" "${SKILLS_SOURCE_DIR}/${skill}/SKILL.md" 2>/dev/null || true)"
                if [[ -n "$diff_output" ]]; then
                    echo -e "    ${DIM}Changes in SKILL.md:${NC}"
                    echo "$diff_output" | head -20 | sed 's/^/    /'
                    local total_lines
                    total_lines="$(echo "$diff_output" | wc -l | tr -d ' ')"
                    if [[ $total_lines -gt 20 ]]; then
                        echo -e "    ${DIM}... ($(( total_lines - 20 )) more lines)${NC}"
                    fi
                fi
            fi
        else
            echo -e "  • ${skill} ${GREEN}v${src_ver}${NC} ${DIM}(new)${NC}"
        fi
    done

    echo ""
    read -rp "Proceed? [y/N] " confirm
    [[ "$confirm" != "y" && "$confirm" != "Y" ]] && { echo "Cancelled."; return; }

    mkdir -p "$SKILLS_TARGET_DIR"
    local count=0
    for skill in "${selected_skills[@]}"; do
        install_skill_dir "$skill"
        ((count++))
        echo -e "  ${GREEN}✓${NC} Installed ${BOLD}${skill}${NC}"
    done

    echo ""
    echo -e "${GREEN}Done! ${count} skill(s) installed/updated.${NC}"
    echo -e "${DIM}Installed to project-local .agents/skills.${NC}"
}

# ─── Remove ───

do_remove() {
    echo ""
    echo -e "${BOLD}Installed skills:${NC}"
    echo ""

    local installed
    read -ra installed <<< "$(get_installed_skills)"

    if [[ ${#installed[@]} -eq 0 || ( ${#installed[@]} -eq 1 && -z "${installed[0]}" ) ]]; then
        echo -e "  ${YELLOW}No skills installed in ${SKILLS_TARGET_DIR}${NC}"
        return
    fi

    local i=1
    declare -A skill_map
    for skill in "${installed[@]}"; do
        local ver
        ver="$(get_version "${SKILLS_TARGET_DIR}/${skill}")"
        printf "  ${BOLD}[%d]${NC} %-14s ${DIM}v%s${NC}\n" "$i" "$skill" "$ver"
        skill_map[$i]="$skill"
        ((i++))
    done

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

    local installed
    read -ra installed <<< "$(get_installed_skills)"

    if [[ ${#installed[@]} -eq 0 || ( ${#installed[@]} -eq 1 && -z "${installed[0]}" ) ]]; then
        echo -e "  ${YELLOW}No skills installed in ${SKILLS_TARGET_DIR}${NC}"
        return
    fi

    declare -A category_skills
    local categories=()

    for skill in "${installed[@]}"; do
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
