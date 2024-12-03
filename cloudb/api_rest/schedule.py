from django_q.models import Schedule
from datetime import datetime, timedelta, date, time

DAYS_OF_WEEK_PT = {
    "segunda": 0,
    "terça": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sábado": 5,
    "domingo": 6,
}

def process_schedule(raw_intervals, raw_repetition, func_name, func_args=None, func_kwargs=None):
    """
    Cria agendamentos no Django-Q2 com base nos dados fornecidos.

    :param raw_intervals: Lista de intervalos de tempo, ex. [{"inicio": "05:19", "fim": "08:52"}].
    :param raw_repetition: Dicionário com tipo de repetição e dias, 
                           ex. {"type": "weekly", "days": ["segunda", "quarta"]}.
    :param func_name: Nome da função a ser agendada.
    :param func_args: Argumentos posicionais para a função (opcional).
    :param func_kwargs: Argumentos nomeados para a função (opcional).
    """
    # Parse repetition data
    repetition_type = raw_repetition.get("type")
    repetition_days = raw_repetition.get("days", [])

    # Converter dias da semana para números (0-6)
    repetition_days = [DAYS_OF_WEEK_PT[day.lower()] for day in repetition_days]

    # Processar cada intervalo
    for interval in raw_intervals:
        start_time = datetime.strptime(interval["inicio"], "%H:%M").time()
        end_time = datetime.strptime(interval["fim"], "%H:%M").time()

        if repetition_type == "weekly" and repetition_days:
            print("Agendamento semanal")
            # Agendamento semanal para dias específicos da semana
            today = datetime.now().date()
            for day in repetition_days:
                # Calcular a próxima ocorrência do dia da semana
                delta_days = (day - today.weekday() + 7) % 7
                next_date = today + timedelta(days=delta_days)

                start_datetime = datetime.combine(next_date, start_time)
                end_datetime = datetime.combine(next_date, end_time)

                Schedule.objects.create(
                    func=func_name,
                    args=func_args or [],
                    kwargs=func_kwargs or {},
                    schedule_type=Schedule.WEEKLY,
                    next_run=start_datetime
                )
                Schedule.objects.create(
                    func=func_name,
                    args=func_args or [],
                    kwargs=func_kwargs or {},
                    schedule_type=Schedule.WEEKLY,
                    next_run=end_datetime
                )

        elif repetition_type == "daily":
            print("Agendamento diário")
            # Agendamento diário
            Schedule.objects.create(
                func=func_name,
                args=func_args or [],
                kwargs=func_kwargs or {},
                schedule_type=Schedule.DAILY,
                next_run=datetime.combine(datetime.now().date(), start_time)
            )
            Schedule.objects.create(
                func=func_name,
                args=func_args or [],
                kwargs=func_kwargs or {},
                schedule_type=Schedule.DAILY,
                next_run=datetime.combine(datetime.now().date(), end_time)
            )

        elif repetition_type == "specific-days":
            print("Agendamento para dias específicos:", repetition_days)
            # Agendamento para datas específicas fornecidas
            specific_dates = raw_repetition.get("dates", [])
            for specific_date in specific_dates:
                specific_date_obj = datetime.strptime(specific_date, "%Y-%m-%d").date()

                start_datetime = datetime.combine(specific_date_obj, start_time)
                end_datetime = datetime.combine(specific_date_obj, end_time)

                Schedule.objects.create(
                    func=func_name,
                    args=func_args or [],
                    kwargs=func_kwargs or {},
                    schedule_type=Schedule.ONCE,
                    next_run=start_datetime
                )
                Schedule.objects.create(
                    func=func_name,
                    args=func_args or [],
                    kwargs=func_kwargs or {},
                    schedule_type=Schedule.ONCE,
                    next_run=end_datetime
                )

        else:
            print("Tipo de repetição não suportado:", repetition_type)
            return False
    return True
