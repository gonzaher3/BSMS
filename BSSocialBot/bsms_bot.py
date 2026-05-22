import datetime
import re
allowed_courses = ["CMSC401", "CMSC411", "CMSC412", "CMSC414", "CMSC416", "CMSC417", "CMSC420", "CMSC421", "CMSC422", "CMSC423", "CMSC424", "CMSC425", "CMSC426", "CMSC427", "CMSC430", "CMSC433", "CMSC434", "CMSC435", "CMSC436", "CMSC451", "CMSC452", "CMSC454", "CMSC456", "MATH456", "CMSC457", "CMSC460", "AMSC460", "CMSC462", "CMSC466", "AMSC466", "CMSC470", "CMSC471", "CMSC472", "CMSC473", "CMSC474", "CMSC475", "MATH475", "CMSC477"]

def normalize_semester_code(code):
    if not isinstance(code, str):
        return None
    code = code.strip().upper()
    if len(code) == 4 and code[:2] in ["FA", "SP"]:
        try:
            year = int(code[2:])
            if year < 100:
                year += 2000
            return code[:2] + str(year)
        except ValueError:
            return None
    elif len(code) == 6 and code[:2] in ["FA", "SP"]:
        try:
            int(code[2:])
            return code
        except ValueError:
            return None
    return None


def get_semester_start_date(semester_code):
    semester_code = normalize_semester_code(semester_code)
    if semester_code is None:
        return None
    try:
        year = int(semester_code[-4:])
        return datetime.date(year, 8,
                             30) if "FA" in semester_code else datetime.date(
                                 year, 1, 30)
    except ValueError:
        return None


def semesters_between(start_code, end_code):
    semesters = ["SP", "FA"]
    s_term, s_year = start_code[:2], int(start_code[-4:])
    e_term, e_year = end_code[:2], int(end_code[-4:])
    return (e_year - s_year) * 2 + (semesters.index(e_term) -
                                    semesters.index(s_term))


def get_next_semester_code(semester_code):
    term, year = semester_code[:2], int(semester_code[-4:])
    return f"SP{year + 1}" if term == "FA" else f"FA{year}"


def get_ms_app_sem(semester_code):
    term, year = semester_code[:2], int(semester_code[-4:])
    return semester_code if term == "FA" else f"FA{year - 1}"


def get_previous_semester(semester_code):
    term, year = semester_code[:2], int(semester_code[-4:])
    return f"FA{year - 1}" if term == "SP" else f"SP{year}"


def is_earlier_semester(sem1, sem2):
    term1, year1 = sem1[:2], int(sem1[-4:])
    term2, year2 = sem2[:2], int(sem2[-4:])
    return year1 < year2 or (year1 == year2 and term1 == "SP"
                             and term2 == "FA")


def get_two_semesters_prior(semester_code):
    semesters = ["SP", "FA"]
    term = semester_code[:2]
    year = int(semester_code[-4:])
    index = semesters.index(term)
    index -= 2
    while index < 0:
        index += 2
        year -= 1
    return f"{semesters[index]}{year}"


def validate_course(course, existing_courses):
    warnings = []

    # Check valid format
    valid_pattern = re.compile(r"^(CMSC|MATH|STAT|AMSC)\d{3}[A-Z]*$")
    if not valid_pattern.match(course):
        warnings.append(
            f"❌ {course} is not a valid course code format (e.g., CMSC420, STAT410)."
        )
        return warnings

    level = course[4]
    
    if any(c == course for c in existing_courses):
        warnings.append(f"❌ You have already entered {course}.")
    # Disallowed courses
    elif level == "1":
        warnings.append(
            f"❌ {course} is a 100-level course and NOT eligible for the combined BS/MS form."
        )
    elif level == "2":
        warnings.append(
            f"❌ {course} is a 200-level course and NOT eligible for the combined BS/MS form."
        )
    elif level == "3":
        warnings.append(
            f"❌ {course} is a 300-level course and NOT eligible for the combined BS/MS form."
        )
    elif level == "6" or level == "7" or level == "8":
        warnings.append(
            f"❌ {course} is a graduate-level course. Talk to your CS advisor to discuss the process for policy exception requests."
        )
    elif course == "CMSC412":
        warnings.append(
            f"❌ {course} is a 4-credit course, and you can only double count two courses totaling 7 credits, since the max double-count cannot exceed 9 credits. Please select a different course. Speak with your advisor if you would like to use CMSC412"
        )
    elif course == "STAT426":
        warnings.append(
        f"❌ {course} Credit only granted for STAT426 OR CMSC320.  You will lose credit for CMSC320 if you already taken the course."
    )
    elif course == "MATH461":
        warnings.append(
        f"❌ {course} Credit only granted for MATH240, MATH341 or MATH461.  You will lose credits if you already taken MATH240 or MATH341."
    )
    elif course.startswith("CMSC") and course not in allowed_courses:
        warnings.append(
            f"❌ {course} is not a valid course for the combined BS/MS form. Please enter a different course."
        )
    elif course.startswith(("AMSC", "STAT", "MATH")) and any(
            c.startswith(("AMSC", "STAT", "MATH")) for c in existing_courses):
        warnings.append(
            f"❌ {course} is an AMSC/STAT/MATH course. Only one such course can be included in the 9-credit double-count limit."
        )

    return warnings


def handle_step(session_data, message):
    # Prevent crashing if step is None (user not eligible)
    step = session_data.get("step")
    if step is None:
        return "❌ You are not eligible to continue. Restart the tool if needed.", session_data

    responses = session_data.get("responses", {})

    # Step 0: CS Major Check
    if step == 0:
        if message.lower() not in ["yes", "no"]:
            return "❌ Are you a CS major at UMD? (yes/no)", session_data
        if message.lower() != "yes":
            return "❌ Only CS majors are eligible for the Combined BS/MS Program.", {
                "step": None,
                "responses": {}
            }
        responses["is_cs_major"] = message
        session_data["step"] = 1
        return ("Q1. What is your current level of CS courses?\n\n"
                "1. Completed CMSC330 and CMSC351\n"
                "2. Currently in CMSC330 and/or CMSC351\n"
                "3. Currently in CMSC216 and/or CMSC250\n"
                "4. Taking CMSC131 or CMSC132", session_data)

    # Step 1: CS level
    elif step == 1:
        if message not in ["1", "2", "3", "4"]:
            return ("❌ Please choose 1–4.\n\n"
                    "Q1. What is your current level of CS courses?\n"
                    "1. Completed CMSC330 and CMSC351\n"
                    "2. Currently in CMSC330 and/or CMSC351\n"
                    "3. Currently in CMSC216 and/or CMSC250\n"
                    "4. Taking CMSC131 or CMSC132", session_data)
        if message == "4":
            return "⏳ Please return to this tool after completing CMSC132.", None
        responses["cs_level"] = message
        session_data["step"] = 2
        return "✅ You can proceed.\n\n Q2: When do you plan to graduate? (e.g., FA2026 or SP27)", session_data

    # Step 2: Graduation semester
    elif step == 2:
        grad_sem = normalize_semester_code(message)
        if not grad_sem or not get_semester_start_date(grad_sem):
            return "❌ Invalid format. Use FA2026 or SP2026 (or short format like SP27).", session_data
        today = datetime.date.today()
        current_sem = "FA" + str(
            today.year) if today.month >= 6 else "SP" + str(today.year)
        responses["grad_sem"] = grad_sem
        responses["ms_app_sem"] = get_ms_app_sem(grad_sem)
        responses["ms_start_sem"] = get_next_semester_code(grad_sem)
        responses["form_submission_sem"] = get_previous_semester(grad_sem)
        responses["credit_check_sem"] = get_two_semesters_prior(grad_sem)
        session_data["responses"] = responses
        if semesters_between(current_sem, grad_sem) < 2:
            session_data["step"] = "2a"
            return "⚠️ If you are graduating within 1 or 2 semesters, we strongly advise you to speak with your advisor ASAP and not rely on this tool alone. Do you accept and understand that this tool is only a guideline and you are ultimately responsible for working with your advisor for your personalized plan? If yes, please type “OK” and hit enter to continue using this tool.", session_data
        session_data["step"] = 3
        return "Q3: What is your current GPA? (e.g., 3.65)", session_data

    # Step 2a: Graduation warning path
    elif step == "2a":
        if message.strip().upper() != "OK":
            return "❌ Please type 'OK' to continue.", session_data
        session_data["step"] = 3
        return "Q3: What is your current GPA? (e.g., 3.65)", session_data
    # Step 3: GPA
    elif step == 3:
        try:
            gpa = float(message)
            if not (0.0 <= gpa <= 4.0):
                return "❌ GPA must be between 0.0 and 4.0.", session_data
        except ValueError:
            return "❌ Please enter a numeric GPA (e.g., 3.65).", session_data
        responses["gpa"] = gpa
        session_data["responses"] = responses
        session_data["step"] = 4
        msg = "⚠️ GPA is below 3.5. The program requires GPA ≥ 3.5." if gpa < 3.5 else "✅ GPA meets requirement."
        return msg + f"\n\nQ4: Will you finish Gen Eds by {responses['credit_check_sem']}? (yes/no)", session_data

    # Step 4: Gen Ed completion
    elif step == 4:
        if message.lower() not in ["yes", "no"]:
            return f"❌ Please answer 'yes' or 'no'. Will you finish Gen Eds by {responses['credit_check_sem']}?", session_data
        responses["gen_ed_complete"] = message.lower()
        session_data["responses"] = responses
        if message.lower() == "yes":
            session_data["step"] = 5
            return f"Q5: How many total credits will you have by {responses['credit_check_sem']}?", session_data
        else:
            session_data["step"] = "4a"
            return "How many Gen Ed credits will you have left by then? (Enter a number)", session_data

    # Step 4a: Remaining Gen Ed credits
    elif step == "4a":
        try:
            credits_left = int(message)
            if not (0 <= credits_left <= 30):
                return "❌ Enter a number between 0 and 30.", session_data
        except ValueError:
            return "❌ Enter a valid whole number.", session_data
        responses["gen_ed_credits_remaining"] = credits_left
        session_data["responses"] = responses
        session_data["step"] = 5
        return f"{'⚠️ You must have ≤6 Gen Ed credits remaining.' if credits_left > 6 else '✅ Gen Ed credit load acceptable.'}\n\nQ5: How many total credits will you have by {responses['credit_check_sem']}?", session_data

    # Step 5: Total credits
    elif step == 5:
        try:
            credits = int(message)
            if not (0 <= credits <= 180):
                return "❌ Enter a number between 0 and 180.", session_data
        except ValueError:
            return "❌ Enter a valid whole number.", session_data
        responses["total_credits_by_check"] = credits
        session_data["responses"] = responses

        if credits < 90:
            session_data["step"] = "5_warn"
            return (
                "⚠️ You must have at least 90 credits by 2 semesters before graduation.\n\n"
                "Hit OK to continue anyway.", session_data)
        session_data["step"] = 6
        return (
            "Q6: You can use up to 9 credits for double counting toward BS/MS programs.\n\n"
            "List three different 400+ level CMSC (or MATH/STAT/AMSC) courses.\n\n"
            "Reply 'OK' to begin entering your courses one by one.",
            session_data)
    # Step 5 warning path
    elif step == "5_warn":
        if message.strip().upper() != "OK":
            return "❌ Please type 'OK' to continue.", session_data
        session_data["step"] = 6
        return (
            "Q6: You can use up to 9 credits for double counting toward BS/MS programs.\n\n"
            "List three 400+ level CMSC (or MATH/STAT/AMSC) courses one by one.\n\n"
            "Hit OK to continue!", session_data)

    # Step 6: Course input
    elif step == 6:
        if message.strip().upper() != "OK":
            return "❌ Please type 'OK' to continue.", session_data
        # User typed OK → move to course entry
        session_data["step"] = "6a"
        session_data["responses"]["course_list"] = []
        return ("Hit Enter after typing your first course:", session_data)

    elif step in ["6a", "6b", "6c"]:
        course = message.strip().upper()
        warnings = validate_course(course,
                                   session_data["responses"]["course_list"])

        # Invalid format
        if "❌" in "".join(warnings):
            return "\n".join(
                warnings
            ) + f"\n\nEnter your {'first' if step=='6a' else 'second' if step=='6b' else 'third'} course again:", session_data

        session_data["responses"]["course_list"].append(course)
        warning_msg = "\n".join(warnings) if warnings else "✅ Course accepted."

        if step == "6a":
            session_data["step"] = "6b"
            return warning_msg + "\n\nEnter your second course:", session_data
        elif step == "6b":
            session_data["step"] = "6c"
            return warning_msg + "\n\nEnter your third course:", session_data
        else:
            session_data["step"] = 7
            return warning_msg + "\n\n✅ Course selection complete.\n\nQ7: Do you already have a research topic?\n1. Yes, working with CS faculty\n2. Yes, need to find CS faculty\n3. No, still looking", session_data

    # Step 7: Research topic
    elif step == 7:
        if message not in ["1", "2", "3"]:
            return "❌ Please enter 1, 2, or 3.\n\nQ7. Do you already have a research topic?", session_data
        responses["research_topic"] = message
        session_data["responses"] = responses
        session_data["step"] = 8
        return "Q8. Do you plan to Study Abroad? (yes/no)", session_data

    # Step 8: Study abroad
    elif step == 8:
        if message.lower() not in ["yes", "no"]:
            return "❌ Please answer 'yes' or 'no'. Do you plan to Study Abroad?", session_data
        responses["study_abroad"] = message.lower()
        session_data["responses"] = responses
        if message.lower() == "no":
            session_data["step"] = 9
            return handle_step(session_data, "")
        else:
            session_data["step"] = "8a"
            return "Which semester do you plan to study abroad? (e.g., FA2026 or SP27)", session_data

    elif step == "8a":
        abroad_sem = normalize_semester_code(message)
        if not abroad_sem:
            return "❌ Please enter a valid semester code like FA2026 or SP27.", session_data
        elif not is_earlier_semester(abroad_sem, responses["grad_sem"]):
            return "❌ Please enter a semester before your graduation semester.", session_data
        else:
            responses["abroad_sem"] = abroad_sem
            session_data["responses"] = responses
            session_data["step"] = 9
            return handle_step(session_data, "")

    # Step 9: Final checklist
    elif step == 9:
        grad_sem = responses.get("grad_sem")
        ms_app_sem = responses.get("ms_app_sem")
        ms_start = responses.get("ms_start_sem")
        form_due = responses.get("form_submission_sem")
        gpa = responses.get("gpa", 0.0)
        gen_ed_ok = responses.get("gen_ed_complete") == "yes" or responses.get(
            "gen_ed_credits_remaining", 0) <= 6
        credit_ok = responses.get("total_credits_by_check", 0) >= 90
        research = responses.get("research_topic")
        abroad = responses.get("study_abroad") == "yes"
        abroad_sem = responses.get("abroad_sem", "")
        courses = responses.get("course_list", [])

        # Count course warnings
        course_warnings = 0
        for c in courses:
            ws = validate_course(c, [])
            course_warnings += sum(1 for w in ws if w.startswith("⚠️"))

        checklist = []
        checklist.append("- ✅ GPA ≥ 3.5" if gpa >=
                         3.5 else "- ❌ GPA below 3.5")
        checklist.append("- ✅ 90+ credits by 2 semesters prior"
                         if credit_ok else "- ❌ Less than 90 credits")
        checklist.append("- ✅ Gen Eds ≤6 credits remaining"
                         if gen_ed_ok else "- ❌ Too many Gen Eds remaining")
        checklist.append("- ✅ Research topic and advisor secured" if research
                         == "1" else "- ⚠️ Work on research/advisor")

        if courses:
            if course_warnings > 0:
                checklist.append(
                    f"- ⚠️ {course_warnings} course warning(s). See an advisor to plan course selection properly."
                )
            else:
                checklist.append(
                    f"- ✅ {len(courses)} courses selected and validated")

        # Course-specific warnings
        if "CMSC412" in courses:
            checklist.append("- ⚠️ CMSC412: limits form to 2 courses")
        if any(c.startswith("CMSC498") for c in courses):
            checklist.append("- ⚠️ CMSC498 courses not allowed")
        if any(c in ["CMSC320", "CMSC335"] for c in courses):
            checklist.append("- ⚠️ CMSC320/CMSC335 not allowed")
        if any(c.startswith(("CMSC6", "CMSC7")) for c in courses):
            checklist.append("- ⚠️ CMSC6XX/7XX require departmental exception")
        if abroad and abroad_sem:
            checklist.append(f"- 🌍 Study Abroad planned: {abroad_sem}")
            if semesters_between(abroad_sem, grad_sem) <= 2:
                checklist.append(
                    "- ⚠️ Study Abroad close to graduation — transfer credits may not count"
                )

        summary = [
            "📋 --- YOUR PERSONALIZED BS/MS PLAN ---",
            f"🎓 Graduation Semester: {grad_sem}",
            f"📄 Submit MS Application: {ms_app_sem}",
            f"➡️ Start MS Program: {ms_start}",
            f"📚 Take 3 courses for BS/MS in {form_due}",
            f"📝 Submit combined form in: {form_due}",
            "🗓 Grad School Deadlines: Fall - Dec prior | Spring - Sep prior",
            "", "✅ CHECKLIST"
        ] + checklist + [
            "", "💬 Got Questions?",
            "- Talk to your CS advisor for help with the 3 combined courses",
            "- For all other inquiries, talk to the grad office coordinator",
            "", "🎉 Done! Thanks for using the UMD CS BS/MS Planner.", "",
            "⚠️ Disclaimer: This program is a guideline, please consult with your assigned CS advisor for better guidance."
        ]

        return "\n".join(summary), None
