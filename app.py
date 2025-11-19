import os
import sqlite3
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from datetime import datetime
from typing import Optional, List, Tuple

from portal_db import (
    init_portal_db,
    insert_portal_request,
    get_all_portal_requests,
    update_portal_status,
    delete_portal_request,
)

from portal_db import init_portal_db, insert_portal_request, get_all_portal_requests
from cert_db import init_cert_db, insert_cert_request, get_all_cert_requests
from ecp_db import init_ecp_db, insert_ecp_request, get_all_ecp_requests
from event_db import init_event_db, insert_event_request, get_all_event_requests

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me-in-production")

# Инициализация баз при старте
init_portal_db()
init_cert_db()
init_ecp_db()
init_event_db()

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "GTYBC")  # для демо GTYBC[th]

@app.route("/")
def index():
    return render_template("index.html", title="Университетский сервис")


# ---------- 1. Обработка заявок на портал ----------

@app.route("/portal-request", methods=["GET", "POST"])
def portal_request():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        faculty = request.form.get("faculty", "").strip()
        portal_section = request.form.get("portal_section", "").strip()
        issue_type = request.form.get("issue_type", "").strip()
        description = request.form.get("description", "").strip()

        if not full_name or not description:
            flash("Пожалуйста, заполните ФИО и описание проблемы.", "error")
            return redirect(url_for("portal_request"))

        # В реальном мини-приложении сюда можно добавить user_id из WebApp.initData
        insert_portal_request(
            user_id=None,
            full_name=full_name,
            email=email,
            phone=phone,
            faculty=faculty,
            portal_section=portal_section,
            issue_type=issue_type,
            description=description,
        )

        flash("Заявка отправлена. Администратор портала обработает её в ближайшее время.", "success")
        return redirect(url_for("index"))

    return render_template(
        "portal_request.html",
        title="Заявка на портал",
        header="Заявка на портал",
        show_back=True,
    )


# --- Админ: логин и просмотр заявок из отдельной БД ---
@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Вы вышли из админ-панели.", "success")
    return redirect(url_for("index"))

@app.before_request
def protect_admin_routes():
    # защищаем все урлы, начинающиеся с /admin,
    # кроме страницы логина
    if request.path.startswith("/admin") and not request.path.startswith("/admin/login"):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))

@app.route("/admin/event-requests")
def admin_event_requests():
    if not session.get("is_admin"):
        flash("Требуется авторизация администратора.", "error")
        return redirect(url_for("admin_login"))

    requests_list = get_all_event_requests()
    return render_template(
        "admin_event_list.html",
        title="Мероприятия (мультимедиа)",
        header="Мультимедийные мероприятия",
        show_back=True,
        requests_list=requests_list,
    )

@app.route("/admin/ecp-requests")
def admin_ecp_requests():
    if not session.get("is_admin"):
        flash("Требуется авторизация администратора.", "error")
        return redirect(url_for("admin_login"))

    requests_list = get_all_ecp_requests()
    return render_template(
        "admin_ecp_list.html",
        title="Запись на ЭЦП",
        header="Запись на ЭЦП",
        show_back=True,
        requests_list=requests_list,
    )

@app.route("/event-multimedia", methods=["GET", "POST"])
def event_multimedia():
    roles = [
        "Студент",
        "Сотрудник",
        "Студсовет / студорганизация",
        "Подразделение университета",
        "Внешний организатор (по согласованию)",
    ]

    event_types = [
        "Лекция / семинар",
        "Конференция / круглый стол",
        "Культурное мероприятие (концерт, творческий вечер)",
        "Презентация / защита проекта",
        "Конкурс / олимпиада",
        "Другое",
    ]

    audience_types = [
        "Внутреннее (для студентов / сотрудников вуза)",
        "Открытое (для внешних гостей)",
        "Смешанная аудитория",
    ]

    participants_ranges = [
        "до 20 человек",
        "20–50 человек",
        "50–100 человек",
        "100–200 человек",
        "200+ человек",
    ]

    multimedia_options = [
        "Проектор / экран",
        "Акустическая система (звук)",
        "Радиомикрофоны",
        "Проводные микрофоны",
        "Запись видео",
        "Онлайн-трансляция",
        "Фоновая музыка",
        "Технический специалист на площадке",
        "Другое (указать в комментарии)",
    ]

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "").strip()
        event_title = request.form.get("event_title", "").strip()
        event_type = request.form.get("event_type", "").strip()
        audience_type = request.form.get("audience_type", "").strip()
        event_date = request.form.get("event_date", "").strip()
        start_time = request.form.get("start_time", "").strip()
        end_time = request.form.get("end_time", "").strip()
        location = request.form.get("location", "").strip()
        expected_participants = request.form.get("expected_participants", "").strip()
        multimedia_needs_list = request.form.getlist("multimedia_needs")
        multimedia_needs = ", ".join(multimedia_needs_list) if multimedia_needs_list else ""
        needs_recording = request.form.get("needs_recording", "").strip()
        needs_streaming = request.form.get("needs_streaming", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        comment = request.form.get("comment", "").strip()

        # Простая обязательная валидация
        if not (full_name and event_title and event_date and start_time and phone):
            flash("Заполните ФИО, название мероприятия, дату, время начала и телефон.", "error")
            return redirect(url_for("event_multimedia"))

        insert_event_request(
            full_name=full_name,
            role=role,
            event_title=event_title,
            event_type=event_type,
            audience_type=audience_type,
            event_date=event_date,
            start_time=start_time,
            end_time=end_time,
            location=location,
            expected_participants=expected_participants,
            multimedia_needs=multimedia_needs,
            needs_recording=needs_recording,
            needs_streaming=needs_streaming,
            email=email,
            phone=phone,
            comment=comment,
        )

        flash("Заявка на мультимедийное сопровождение мероприятия отправлена.", "success")
        return redirect(url_for("index"))

    return render_template(
        "event_multimedia.html",
        title="Заявка на мероприятие",
        header="Мультимедийное сопровождение",
        show_back=True,
        roles=roles,
        event_types=event_types,
        audience_types=audience_types,
        participants_ranges=participants_ranges,
        multimedia_options=multimedia_options,
    )

@app.route("/admin/cert-requests")
def admin_cert_requests():
    if not session.get("is_admin"):
        flash("Требуется авторизация администратора.", "error")
        return redirect(url_for("admin_login"))

    requests_list = get_all_cert_requests()
    return render_template(
        "admin_cert_list.html",
        title="Заявки на справки",
        header="Заявки на справки",
        show_back=True,
        requests_list=requests_list,
    )

@app.route("/admin")
def admin_home():
    if not session.get("is_admin"):
        flash("Требуется авторизация администратора.", "error")
        return redirect(url_for("admin_login"))

    return render_template(
        "admin_home.html",
        title="Админ-панель",
        header="Админ-панель",
        show_back=True,
    )

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_home"))
        flash("Неверный пароль администратора.", "error")
        return redirect(url_for("admin_login"))

    return render_template(
        "portal_admin_login.html",
        title="Вход администратора",
        header="Админ-панель",
        show_back=True,
    )


@app.route("/admin/portal-requests")
def portal_admin_list():
    if not session.get("is_admin"):
        flash("Требуется авторизация администратора.", "error")
        return redirect(url_for("admin_login"))

    requests_list = get_all_portal_requests()
    return render_template(
        "portal_admin_list.html",
        title="Заявки на портал",
        header="Заявки на портал",
        show_back=True,
        requests_list=requests_list,
    )

@app.route("/admin/portal-requests/<int:req_id>/status", methods=["POST"])
def portal_admin_update_status(req_id):
    if not session.get("is_admin"):
        flash("Требуется авторизация администратора.", "error")
        return redirect(url_for("admin_login"))

    status = request.form.get("status", "").strip()
    allowed_statuses = ["ожидает", "в процессе", "выполнено"]

    if status not in allowed_statuses:
        flash("Некорректный статус.", "error")
    else:
        update_portal_status(req_id, status)
        flash(f"Статус заявки #{req_id} обновлён.", "success")

    return redirect(url_for("portal_admin_list"))


@app.route("/admin/portal-requests/<int:req_id>/delete", methods=["POST"])
def portal_admin_delete(req_id):
    if not session.get("is_admin"):
        flash("Требуется авторизация администратора.", "error")
        return redirect(url_for("admin_login"))

    delete_portal_request(req_id)
    flash(f"Заявка #{req_id} удалена.", "success")
    return redirect(url_for("portal_admin_list"))

# ---------- 2. Заказ справок для студентов ----------

@app.route("/student-certificate", methods=["GET", "POST"])
def student_certificate():
    certificate_types = [
        "Справка об обучении",
        "Справка о периоде обучения",
        "Академическая справка",
        "Справка для военкомата",
        "Справка для соцзащиты",
        "Справка для общежития",
        "Иное (указать в комментарии)",
    ]

    forms_of_study = ["Очная", "Очно-заочная", "Заочная"]
    funding_types = ["Бюджет", "Договор (платное обучение)"]
    languages = ["Русский", "Английский"]
    pickup_methods = [
        "Получить лично в деканате",
        "Получить в МФЦ/единый деканат",
        "Получить в электронном виде (скан на e-mail)",
    ]
    courses = ["1", "2", "3", "4", "5", "6"]

    if request.method == "POST":
        cert_type = request.form.get("cert_type")
        full_name = request.form.get("full_name", "").strip()
        birth_date = request.form.get("birth_date", "").strip()
        student_id = request.form.get("student_id", "").strip()
        faculty = request.form.get("faculty", "").strip()
        program = request.form.get("program", "").strip()
        course = request.form.get("course", "").strip()
        form_of_study = request.form.get("form_of_study", "").strip()
        funding = request.form.get("funding", "").strip()
        period_from = request.form.get("period_from", "").strip()
        period_to = request.form.get("period_to", "").strip()
        language = request.form.get("language", "").strip()
        pickup_method = request.form.get("pickup_method", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        comment = request.form.get("comment", "").strip()

        if not (full_name and cert_type and faculty and course):
            flash("Заполните как минимум ФИО, тип справки, факультет и курс.", "error")
            return redirect(url_for("student_certificate"))

        insert_cert_request(
            cert_type=cert_type,
            full_name=full_name,
            birth_date=birth_date,
            student_id=student_id,
            faculty=faculty,
            program=program,
            course=course,
            form_of_study=form_of_study,
            funding=funding,
            period_from=period_from,
            period_to=period_to,
            language=language,
            pickup_method=pickup_method,
            email=email,
            phone=phone,
            comment=comment,
        )

        flash("Заявка на справку отправлена. О готовности уведомят дополнительно.", "success")
        return redirect(url_for("index"))

    return render_template(
        "student_certificate.html",
        title="Заказ справки",
        header="Заказ справки",
        show_back=True,
        certificate_types=certificate_types,
        forms_of_study=forms_of_study,
        funding_types=funding_types,
        languages=languages,
        pickup_methods=pickup_methods,
        courses=courses,
    )

@app.route("/ecp-support", methods=["GET", "POST"])
def ecp_support():
    roles = [
        "Студент",
        "Сотрудник",
        "Абитуриент",
        "Иное физическое лицо",
    ]

    ecp_types = [
        "ЭЦП для физического лица (Госуслуги и др.)",
        "ЭЦП для преподавателя / сотрудника",
        "ЭЦП для работы с университетскими сервисами",
        "ЭЦП для юрлица / ИП (консультация)",
    ]

    offices = [
        "Главный кампус, окно сопровождения ЭЦП",
        "Учебный отдел",
        "Деканат факультета (по предварительному согласованию)",
    ]

    time_slots = [
        "09:00–11:00",
        "11:00–13:00",
        "14:00–16:00",
        "16:00–18:00",
    ]

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        role = request.form.get("role", "").strip()
        ecp_type = request.form.get("ecp_type", "").strip()
        office = request.form.get("office", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()
        time_slot = request.form.get("time_slot", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        passport_last4 = request.form.get("passport_last4", "").strip()
        snils = request.form.get("snils", "").strip()
        comment = request.form.get("comment", "").strip()

        # Простая валидация
        if not (full_name and phone and preferred_date and time_slot):
            flash("Заполните ФИО, телефон, дату и время записи.", "error")
            return redirect(url_for("ecp_support"))

        insert_ecp_request(
            full_name=full_name,
            role=role,
            ecp_type=ecp_type,
            office=office,
            preferred_date=preferred_date,
            time_slot=time_slot,
            email=email,
            phone=phone,
            passport_last4=passport_last4,
            snils=snils,
            comment=comment,
        )

        flash("Заявка на сопровождение по ЭЦП отправлена. С вами свяжутся для подтверждения записи.", "success")
        return redirect(url_for("index"))

    return render_template(
        "ecp_support.html",
        title="Запись на ЭЦП",
        header="Запись на ЭЦП",
        show_back=True,
        roles=roles,
        ecp_types=ecp_types,
        offices=offices,
        time_slots=time_slots,
    )

# ---------- запуск ----------

if __name__ == "__main__":
    app.run(debug=True)