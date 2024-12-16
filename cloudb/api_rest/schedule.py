from django_q.models import Schedule
from datetime import datetime, timedelta, date, time
from .tasks import start, stop, start_vm_result

DAYS_OF_WEEK_PT = {
    "segunda": 0,
    "terça": 1,
    "quarta": 2,
    "quinta": 3,
    "sexta": 4,
    "sábado": 5,
    "domingo": 6,
}


def test_reschedule(schedule_time, repetition):
    """
     Recebe uma data e uma repeticao, se a data for menor do que a data hora atual, retorna uma nova data agendada para a proxima data baseada na repeticao
    """
    today = datetime.now()

    if schedule_time < today:
        if repetition == "daily":
            return schedule_time + timedelta(days=1)
        elif repetition == "weekly":
            return schedule_time + timedelta(weeks=1)

    return schedule_time

def process_schedule(raw_intervals, raw_repetition, schedule_id, func_kwargs=None):

    """
    Cria agendamentos no Django-Q2 com base nos dados fornecidos.

    :param raw_intervals: Lista de intervalos de tempo, ex. [{"inicio": "05:19", "fim": "08:52"}].
    :param raw_repetition: Dicionário com tipo de repetição e dias, 
                           ex. {"type": "weekly", "days": ["segunda", "quarta"]}.
    :param func_name: Nome da função a ser agendada. (start, stop)
    :param func_args: Argumentos posicionais para a função (opcional).
    :param func_kwargs: Argumentos nomeados para a função (opcional).
    """
    # Parse repetition data
    repetition_type = raw_repetition.get("type")
    repetition_days = raw_repetition.get("days", [])

    today = datetime.now().time()

    # Convert days' name in (0-6)
    repetition_days = [DAYS_OF_WEEK_PT[day.lower()] for day in repetition_days]

    # Process each interval 
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

                start_datetime = test_reschedule(datetime.combine(next_date, start_time), repetition_type)
                end_datetime = test_reschedule(datetime.combine(next_date, end_time), repetition_type)


                Schedule.objects.create(
                    name='Start VM',
                    func='api_rest.tasks.start',
                    hook='api_rest.tasks.start_vm_result',
                    args=schedule_id,
                    schedule_type=Schedule.WEEKLY,
                    next_run=start_datetime
                )
                Schedule.objects.create(
                    name='Stop VM',
                    func='api_rest.tasks.stop',
                    hook='api_rest.tasks.stop_vm_result',
                    args=schedule_id,
                    schedule_type=Schedule.WEEKLY,
                    next_run=end_datetime
                )

        elif repetition_type == "daily":
            print("Agendamento diário")
            # Agendamento diário
            Schedule.objects.create(
                name='Start VM',
                func='api_rest.tasks.start',
                hook='api_rest.tasks.start_vm_result',
                args=schedule_id,
                schedule_type=Schedule.DAILY,
                next_run=datetime.combine(datetime.now().date(), start_time)

            )
            Schedule.objects.create(
                name='Stop VM',
                func='api_rest.tasks.stop',
                hook='api_rest.tasks.stop_vm_result',
                args=schedule_id,
                schedule_type=Schedule.DAILY,
                next_run=datetime.combine(datetime.now().date(), end_time)
            )

        elif repetition_type == "specific-days":
            # Agendamento para datas específicas fornecidas
            specific_dates = raw_repetition.get("dates", [])
            for specific_date in specific_dates:
                specific_date_obj = datetime.strptime(specific_date, "%Y-%m-%d").date()

                start_datetime = datetime.combine(specific_date_obj, start_time)
                end_datetime = datetime.combine(specific_date_obj, end_time)

                Schedule.objects.create(
                    name='Start VM',
                    func='api_rest.tasks.start',
                    hook='api_rest.tasks.start_vm_result',
                    args=schedule_id,
                    schedule_type=Schedule.ONCE,
                    next_run=start_datetime
                )
                Schedule.objects.create(
                    name='Stop VM',
                    func='api_rest.tasks.stop',
                    hook='api_rest.tasks.stop_vm_result',
                    args=schedule_id,
                    schedule_type=Schedule.ONCE,
                    next_run=end_datetime
                )

        else:
            print("Tipo de repetição não suportado:", repetition_type)
            return False
    return True
