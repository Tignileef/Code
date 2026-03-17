def read_log_file(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if not lines:
            print("[안내] 로그 파일이 비어 있습니다.")
            return []

        print("=== mission_computer_main.log 전체 내용 ===")
        for line in lines:
            print(line.strip())

        return lines

    except FileNotFoundError:
        print("[오류] mission_computer_main.log 파일을 찾을 수 없습니다.")
        return []
    except PermissionError:
        print("[오류] 파일 접근 권한이 없습니다.")
        return []
    except UnicodeDecodeError:
        print("[오류] 파일 인코딩 문제로 읽을 수 없습니다.")
        return []
    except Exception as e:
        print(f"[오류] 알 수 없는 문제가 발생했습니다: {e}")
        return []


def print_reverse_log(lines):
    if not lines:
        return

    print("\n=== 로그 시간 역순 출력 ===")

    header = lines[0].strip()
    body = lines[1:]

    print(header)
    for line in reversed(body):
        print(line.strip())


def parse_log_line(line):
    parts = line.strip().split(",", 2)
    if len(parts) != 3:
        return None

    return {
        "timestamp": parts[0],
        "level": parts[1],
        "message": parts[2]
    }


def is_problem_log(parsed_log):
    """
    로그 레벨이 INFO여도 실제 사고 의미가 있으면 문제 로그로 본다.
    """
    if not parsed_log:
        return False

    level = parsed_log["level"].upper()
    message = parsed_log["message"].lower()

    if level in ["WARNING", "ERROR", "CRITICAL", "FAIL"]:
        return True

    danger_keywords = [
        "unstable",
        "explosion",
        "explode",
        "fire",
        "leak",
        "failure",
        "fault",
        "overheat",
        "overheating",
        "malfunction",
        "emergency",
        "abort",
        "loss",
        "damaged",
        "damage"
    ]

    return any(keyword in message for keyword in danger_keywords)


def save_problem_lines(lines, output_path):
    if not lines:
        return 0

    header = lines[0]
    body = lines[1:]

    problem_lines = []

    for line in body:
        parsed = parse_log_line(line)
        if is_problem_log(parsed):
            problem_lines.append(line)

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(header)
            file.writelines(problem_lines)

        print("\n=== 문제 로그 저장 완료 ===")
        print(f"저장 파일: {output_path}")
        print(f"저장 건수: {len(problem_lines)}")

    except Exception as e:
        print(f"[오류] 문제 로그 저장 중 문제가 발생했습니다: {e}")

    return len(problem_lines)


def detect_issue_categories(parsed_logs):
    categories = {
        "vibration": [],
        "cooling_temperature": [],
        "thrust": [],
        "guidance_sensor": [],
        "structure_booster": [],
        "telemetry_comm": [],
        "oxygen_tank": [],
        "mission_success": [],
        "shutdown": []
    }

    for log in parsed_logs:
        msg = log["message"].lower()

        if "vibration" in msg:
            categories["vibration"].append(log)

        if "cooling" in msg or "temperature" in msg or "heat" in msg or "overheat" in msg:
            categories["cooling_temperature"].append(log)

        if "thrust" in msg:
            categories["thrust"].append(log)

        if (
            "guidance" in msg
            or "sensor data" in msg
            or "trajectory" in msg
            or "deviating" in msg
            or "navigation" in msg
        ):
            categories["guidance_sensor"].append(log)

        if (
            "structural integrity" in msg
            or "booster assembly" in msg
            or "booster section" in msg
            or "structural damage" in msg
        ):
            categories["structure_booster"].append(log)

        if (
            "telemetry" in msg
            or "signal lost" in msg
            or "communication lost" in msg
            or "communication failure" in msg
            or "link lost" in msg
            or "data loss" in msg
        ):
            categories["telemetry_comm"].append(log)

        if (
            "oxygen" in msg
            or "tank" in msg
            or "unstable" in msg
            or "explosion" in msg
            or "explode" in msg
        ):
            categories["oxygen_tank"].append(log)

        if (
            "mission completed successfully" in msg
            or "mission objectives achieved" in msg
            or "satellite deployment successful" in msg
            or "safely landed" in msg
        ):
            categories["mission_success"].append(log)

        if "powered down" in msg or "shutdown" in msg:
            categories["shutdown"].append(log)

    return categories


def build_issue_summary(categories):
    summary_list = []

    if categories["oxygen_tank"]:
        first = categories["oxygen_tank"][0]
        summary_list.append(
            f"산소탱크 관련 이상은 {first['timestamp']}에 처음 나타났으며, 내용은 '{first['message']}' 입니다."
        )

    if categories["vibration"]:
        first = categories["vibration"][0]
        summary_list.append(
            f"진동 관련 이상은 {first['timestamp']}에 처음 나타났으며, 내용은 '{first['message']}' 입니다."
        )

    if categories["cooling_temperature"]:
        first = categories["cooling_temperature"][0]
        summary_list.append(
            f"냉각/온도 관련 이상은 {first['timestamp']}에 처음 나타났으며, 내용은 '{first['message']}' 입니다."
        )

    if categories["thrust"]:
        first = categories["thrust"][0]
        summary_list.append(
            f"추력 관련 이상은 {first['timestamp']}에 처음 나타났으며, 내용은 '{first['message']}' 입니다."
        )

    if categories["guidance_sensor"]:
        first = categories["guidance_sensor"][0]
        summary_list.append(
            f"유도/센서 관련 이상은 {first['timestamp']}에 처음 나타났으며, 내용은 '{first['message']}' 입니다."
        )

    if categories["structure_booster"]:
        first = categories["structure_booster"][0]
        summary_list.append(
            f"구조/부스터 관련 이상은 {first['timestamp']}에 처음 나타났으며, 내용은 '{first['message']}' 입니다."
        )

    if categories["telemetry_comm"]:
        last = categories["telemetry_comm"][-1]
        summary_list.append(
            f"원격계측/통신 관련 마지막 이상은 {last['timestamp']}에 기록되었으며, 내용은 '{last['message']}' 입니다."
        )

    if categories["mission_success"]:
        last = categories["mission_success"][-1]
        summary_list.append(
            f"임무 성공 관련 로그는 {last['timestamp']}에 확인되었으며, 내용은 '{last['message']}' 입니다."
        )

    if categories["shutdown"]:
        last = categories["shutdown"][-1]
        summary_list.append(
            f"시스템 종료 관련 로그는 {last['timestamp']}에 기록되었으며, 내용은 '{last['message']}' 입니다."
        )

    if not summary_list:
        return "메시지 내용 기준으로 뚜렷한 이상 범주를 찾지 못했습니다."

    return " ".join(summary_list)


def infer_root_cause(categories, warning_count, error_count, critical_count, fail_count, parsed_logs):
    has_vibration = len(categories["vibration"]) > 0
    has_cooling = len(categories["cooling_temperature"]) > 0
    has_thrust = len(categories["thrust"]) > 0
    has_guidance = len(categories["guidance_sensor"]) > 0
    has_structure = len(categories["structure_booster"]) > 0
    has_telemetry = len(categories["telemetry_comm"]) > 0
    has_oxygen = len(categories["oxygen_tank"]) > 0
    has_success = len(categories["mission_success"]) > 0
    has_shutdown = len(categories["shutdown"]) > 0

    oxygen_unstable = any("unstable" in log["message"].lower() for log in categories["oxygen_tank"])
    oxygen_explosion = any(
        "explosion" in log["message"].lower() or "explode" in log["message"].lower()
        for log in categories["oxygen_tank"]
    )

    if has_oxygen and oxygen_unstable and oxygen_explosion and has_success:
        return (
            "로그 흐름상 발사·궤도 진입·위성 배치·착륙까지 임무 자체는 정상적으로 완료된 것으로 보입니다. "
            "다만 임무 성공 이후 산소탱크 불안정 상태가 발생했고, 이후 산소탱크 폭발로 사고가 확대된 것으로 판단됩니다. "
            "즉, 이번 사고의 직접 원인은 산소탱크 계통 이상이며, 성격상 비행 중 사고라기보다 임무 완료 후 또는 회수 단계의 후속 사고에 가깝습니다."
        )

    if has_oxygen and oxygen_explosion:
        return (
            "가장 유력한 직접 원인은 산소탱크 폭발입니다. "
            "폭발 이전의 불안정 상태가 함께 기록되어 있다면, 탱크 압력 이상 또는 저장 계통 불안정이 선행 원인일 가능성이 큽니다."
        )

    if has_vibration and has_cooling and has_thrust and has_guidance and has_structure:
        return (
            "로그 흐름상 가장 유력한 원인은 부스터 또는 기계 계통의 진동 이상이 먼저 발생하고, "
            "이후 냉각 성능 저하와 추력 불안정으로 확대되며, 결과적으로 유도 오류와 구조 손상까지 이어진 복합 장애로 판단됩니다."
        )

    if has_cooling and has_thrust:
        return (
            "가장 유력한 원인은 엔진 냉각 또는 온도 이상으로 보이며, "
            "이 문제가 추력 불안정으로 이어져 비행 안정성을 무너뜨린 것으로 판단됩니다."
        )

    if has_guidance and has_thrust:
        return (
            "가장 유력한 원인은 추력 불안정과 유도 시스템 이상이 동시에 발생한 상황으로 보이며, "
            "이로 인해 계획 궤적 유지에 실패했을 가능성이 큽니다."
        )

    if has_structure and critical_count > 0:
        return (
            "구조 또는 부스터 계통의 이상이 심각 단계까지 진행된 것으로 보이며, "
            "기계적 손상이 사고의 직접 원인일 가능성이 높습니다."
        )

    if has_telemetry and fail_count > 0:
        return (
            "최종적으로 원격계측 또는 통신 손실이 확인되며 임무 실패로 이어졌습니다. "
            "다만 통신 손실은 최종 결과일 가능성이 크고, 실제 근본 원인은 그 이전의 시스템 이상일 수 있습니다."
        )

    if fail_count > 0 or critical_count > 0:
        return (
            "심각한 시스템 이상이 확인되며, 경고와 오류가 누적된 뒤 최종적으로 치명적 장애로 확대된 것으로 판단됩니다."
        )

    if error_count > 0:
        return (
            "로그에 ERROR가 존재하므로 시스템 오류가 분명히 발생했으며, 해당 오류가 사고 또는 장애의 직접 원인일 가능성이 높습니다."
        )

    if warning_count > 0:
        return (
            "현재는 경고 수준의 이상 징후가 확인되며, 즉시 치명적이진 않더라도 후속 점검이 반드시 필요한 상태로 판단됩니다."
        )

    return (
        "모든 로그가 INFO 수준으로 기록되어 있으므로 현재 로그만으로는 직접적인 사고 원인을 특정하기 어렵습니다. "
        "다만 메시지 키워드 분석을 통해 추가적인 이상 여부를 함께 확인할 필요가 있습니다."
    )


def analyze_logs(lines):
    if not lines or len(lines) < 2:
        return {
            "info_count": 0,
            "warning_count": 0,
            "error_count": 0,
            "critical_count": 0,
            "fail_count": 0,
            "problem_count": 0,
            "last_message": "로그 데이터 없음",
            "issue_summary": "분석할 로그가 없습니다.",
            "cause_text": "로그가 없어서 사고 원인을 분석할 수 없습니다."
        }

    body = lines[1:]
    parsed_logs = []

    for line in body:
        item = parse_log_line(line)
        if item:
            parsed_logs.append(item)

    info_count = sum(1 for log in parsed_logs if log["level"] == "INFO")
    warning_count = sum(1 for log in parsed_logs if log["level"] == "WARNING")
    error_count = sum(1 for log in parsed_logs if log["level"] == "ERROR")
    critical_count = sum(1 for log in parsed_logs if log["level"] == "CRITICAL")
    fail_count = sum(1 for log in parsed_logs if log["level"] == "FAIL")
    problem_count = sum(1 for log in parsed_logs if is_problem_log(log))

    last_message = parsed_logs[-1]["message"] if parsed_logs else "로그 데이터 없음"

    categories = detect_issue_categories(parsed_logs)
    issue_summary = build_issue_summary(categories)
    cause_text = infer_root_cause(
        categories,
        warning_count,
        error_count,
        critical_count,
        fail_count,
        parsed_logs
    )

    return {
        "info_count": info_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "critical_count": critical_count,
        "fail_count": fail_count,
        "problem_count": problem_count,
        "last_message": last_message,
        "issue_summary": issue_summary,
        "cause_text": cause_text
    }


def create_markdown_report(analysis, output_path):
    report = f"""# 미션 컴퓨터 로그 분석 보고서

## 1. 분석 목적
mission_computer_main.log 파일을 분석하여 시스템 상태와 사고 원인을 파악한다.

## 2. 로그 수준별 집계
- INFO 개수: {analysis['info_count']}
- WARNING 개수: {analysis['warning_count']}
- ERROR 개수: {analysis['error_count']}
- CRITICAL 개수: {analysis['critical_count']}
- FAIL 개수: {analysis['fail_count']}

## 3. 실제 문제 로그 개수
- 위험 키워드까지 포함한 문제 로그 개수: {analysis['problem_count']}

## 4. 마지막 로그 메시지
{analysis['last_message']}

## 5. 주요 이상 징후 요약
{analysis['issue_summary']}

## 6. 사고 원인 분석
{analysis['cause_text']}

## 7. 결론
로그 수준과 메시지 키워드를 함께 분석한 결과를 바탕으로 시스템 상태와 사고 원인을 추정하였다.
"""

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(report)

        print("\n=== Markdown 보고서 생성 완료 ===")
        print(f"저장 파일: {output_path}")

    except Exception as e:
        print(f"[오류] Markdown 보고서 생성 중 문제가 발생했습니다: {e}")


if __name__ == "__main__":
    log_file = "mission_computer_main.log"
    problem_file = "problem_only.log"
    report_file = "log_analysis.md"

    lines = read_log_file(log_file)
    print_reverse_log(lines)
    save_problem_lines(lines, problem_file)

    analysis = analyze_logs(lines)
    create_markdown_report(analysis, report_file)