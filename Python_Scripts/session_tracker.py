import subprocess
import json
from datetime import datetime, timedelta

POWER_WATTS = 700     # Среднее потребление ПК в Ваттах
PRICE_PER_KWH = 6.0   # Стоимость 1 кВтч в рублях

def get_events(event_ids):
    ids_str = ",".join(map(str, event_ids))
    ps_script = f"Get-WinEvent -FilterHashtable @{{LogName='System';ID={ids_str}}} -ErrorAction SilentlyContinue | Select-Object TimeCreated, ID, Message | ConvertTo-Json"
    result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, encoding='cp1251')
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if not stdout.strip():
        return []
    try:
        data = json.loads(stdout)
        if isinstance(data, dict):
            return [data]
        return data
    except Exception as e:
        print(f"Ошибка при разборе событий: {e}")
        return []

def parse_date(date_str):
    # PowerShell dates look like "/Date(1740181264000)/"
    if "/Date(" in date_str:
        ms = int(date_str.split("(")[1].split(")")[0])
        return datetime.fromtimestamp(ms / 1000.0)
    return datetime.fromisoformat(date_str)

def analyze_sessions():
    # 6005, 1, 12: Startup / System Time Change (Wake)
    # 6006, 6008, 1074, 13: Shutdown / System Time Change (Sleep)
    events = get_events([6005, 6006, 6008, 1074, 1, 12, 13])
    
    if not events:
        return "События не найдены."

    parsed_events = []
    for e in events:
        parsed_events.append({
            'time': parse_date(e['TimeCreated']),
            'id': e['Id']
        })
    
    # Sort events by time ascending
    parsed_events.sort(key=lambda x: x['time'])

    sessions = []
    current_start = None

    for e in parsed_events:
        if e['id'] in [6005, 1, 12]:
            current_start = e['time']
        elif e['id'] in [6006, 6008, 1074, 13] and current_start:
            duration = e['time'] - current_start
            # Ignore sessions shorter than 1 minute (noise)
            if duration > timedelta(minutes=1):
                sessions.append({
                    'start': current_start,
                    'end': e['time'],
                    'duration': duration
                })
            current_start = None

    # Handle ongoing session
    if current_start:
         sessions.append({
                'start': current_start,
                'end': datetime.now(),
                'duration': datetime.now() - current_start,
                'ongoing': True
            })

    return sessions

def generate_report(sessions):
    if isinstance(sessions, str):
        return sessions

    now = datetime.now()
    month_ago = now - timedelta(days=30)
    year_ago = now - timedelta(days=365)

    def get_stats_dict(data):
        if not data:
            return None
        total_time = sum((s['duration'] for s in data), timedelta())
        days = total_time.days
        hours, remainder = divmod(total_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        total_str = f"{days}д {hours}ч {minutes}м"
        
        avg_seconds = total_time.total_seconds() / len(data)
        avg_time = timedelta(seconds=avg_seconds)
        avg_hours, remainder = divmod(avg_time.seconds, 3600)
        avg_minutes, seconds = divmod(remainder, 60)
        avg_str = f"{avg_hours}ч {avg_minutes}м"

        total_hours = total_time.total_seconds() / 3600
        kwh = (total_hours * POWER_WATTS) / 1000
        cost = kwh * PRICE_PER_KWH
        
        return {
            'count': len(data),
            'total': total_str,
            'avg': avg_str,
            'kwh': f"{kwh:.2f}",
            'cost': f"{cost:.2f}"
        }

    # Grouping by month
    monthly_groups = {}
    for s in sessions:
        key = s['start'].strftime('%Y-%m')
        if key not in monthly_groups:
            monthly_groups[key] = []
        monthly_groups[key].append(s)

    sorted_months = sorted(monthly_groups.keys(), reverse=True)

    m_stats = get_stats_dict([s for s in sessions if s['start'] > month_ago])
    y_stats = get_stats_dict([s for s in sessions if s['start'] > year_ago])
    all_stats = get_stats_dict(sessions)

    report = f"# Отчет о сессиях ПК и электричестве\nСформирован: {now.strftime('%d.%m.%Y %H:%M:%S')}\n\n"
    report += f"> [!TIP]\n"
    report += f"> Параметры: Мощность = **{POWER_WATTS}Вт**, Тариф = **{PRICE_PER_KWH}руб/кВтч**\n\n"
    
    report += "## 🌐 Общая статистика\n"
    if all_stats:
        report += f"- Всего сессий: **{all_stats['count']}**\n"
        report += f"- Общее время онлайн: **{all_stats['total']}**\n"
        report += f"- Потрачено энергии: **{all_stats['kwh']} кВтч**\n"
        report += f"- Примерная стоимость: **{all_stats['cost']} руб.**\n"
        first_date = sessions[0]['start'].strftime('%d.%m.%Y')
        report += f"- Логи доступны с: {first_date}\n"

    report += "\n## 📊 Разбивка по месяцам\n"
    report += "| Месяц | Сессий | Время онлайн | Энергия | Стоимость |\n"
    report += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    month_names = {
        '01': 'Январь', '02': 'Февраль', '03': 'Март', '04': 'Апрель',
        '05': 'Май', '06': 'Июнь', '07': 'Июль', '08': 'Август',
        '09': 'Сентябрь', '10': 'Октябрь', '11': 'Ноябрь', '12': 'Декабрь'
    }

    for month_key in sorted_months:
        stats = get_stats_dict(monthly_groups[month_key])
        year, month = month_key.split('-')
        label = f"{month_names[month]} {year}"
        report += f"| {label} | {stats['count']} | {stats['total']} | {stats['kwh']} кВтч | {stats['cost']} руб. |\n"

    report += "\n## 🏆 Топ-10 самых долгих сессий (за всё время)\n"
    report += "| Начало | Конец | Длительность | Стоимость | Статус |\n"
    report += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    # Сортируем по длительности (самые долгие первыми)
    longest_sessions = sorted(sessions, key=lambda x: x['duration'], reverse=True)
    
    for s in longest_sessions[:10]:
        type_str = "Активна" if s.get('ongoing') else "Завершена"
        dur_hours, remainder = divmod(s['duration'].seconds, 3600)
        dur_minutes, seconds = divmod(remainder, 60)
        dur_str = f"{s['duration'].days}д {dur_hours}ч {dur_minutes}м" if s['duration'].days > 0 else f"{dur_hours}ч {dur_minutes}м"
        
        s_total_hours = s['duration'].total_seconds() / 3600
        s_cost = (s_total_hours * POWER_WATTS / 1000) * PRICE_PER_KWH
        
        report += f"| {s['start'].strftime('%d.%m.%Y %H:%M')} | {s['end'].strftime('%H:%M')} | {dur_str} | {s_cost:.2f}р | {type_str} |\n"

    return report

if __name__ == "__main__":
    print("Анализ событий и расчет энергии... (это может занять время)")
    sessions = analyze_sessions()
    report = generate_report(sessions)
    
    with open("session_report.md", "w", encoding='utf-8') as f:
        f.write(report)
    
    print("Report generated: session_report.md")
