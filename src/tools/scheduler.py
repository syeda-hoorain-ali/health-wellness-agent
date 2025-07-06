import os
from typing import Literal, Optional

from agents import RunContextWrapper, function_tool
from datetime import date, datetime, timedelta
from ics import Calendar, Event
from pydantic import BaseModel
from uuid import uuid4

from src.context import UserSessionContext


class ScheduleConfirmation(BaseModel):
    event_id: str
    user_id: int
    frequency: str
    next_occurrence: date
    calendar_file: Optional[str] = None
    confirmation_link: Optional[str] = None


# Function to get timedelta for frequency
def get_timedelta(frequency: Literal["DAILY", "WEEKLY", "MONTHLY"]):
    match frequency:
        case "daily": return timedelta(days=1) 
        case "weekly": return timedelta(weeks=1) 
        case "monthly": return timedelta(days=30) 
    
    raise ValueError("Invalid frequency") 


@function_tool(strict_mode=False)
def checkin_scheduler_local(
    ctx: RunContextWrapper[UserSessionContext],
    user_id: int,
    frequency: Literal["DAILY", "WEEKLY", "MONTHLY"],
    start_date: Optional[date] = None
) -> ScheduleConfirmation:
    """
    Create local iCal file for recurring progress check-ins.
    
    Args:
        user_id: User identifier
        frequency: Recurrence frequency (DAILY, WEEKLY, MONTHLY)
        start_date: Start date for the recurring events (optional, defaults to current date)
    
    Returns:
        ScheduleConfirmation with event details and local file path
    """

    user = ctx.context
    
    # Use current date if no start_date provided
    if start_date is None:
        start_date = date.today()
    
    event_id = str(uuid4())
    next_occurrence = start_date + get_timedelta(frequency)
    
    
    cal = Calendar()
    event = Event(
        name=f"Progress Check-in for {user.name}",
        begin=datetime(start_date.year, start_date.month, start_date.day),
        uid=event_id,
        description=f"",
        duration=timedelta(minutes=15),
    )
    cal.events.add(event)
    
    filename = f"user_{user.uid}_{frequency}_checkin.ics"
    
    with open(filename, "w") as file:
        file.writelines(cal.serialize_iter())
    
    return ScheduleConfirmation(
        user_id=user_id,
        event_id=event_id,
        frequency=frequency,
        next_occurrence=next_occurrence,
        calendar_file=os.path.abspath(filename)
    )
    



import os.path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate_google():
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=0)
    # url, _ = flow.authorization_url()
    # print(url)
    # print(_)
    # webbrowser.open(url, )
    # creds = flow.fetch_token(authorization_response=url)
    
    print(creds)
    return creds


@function_tool(strict_mode=False)
def checkin_scheduler_google(
    ctx: RunContextWrapper[UserSessionContext],
    frequency: Literal["DAILY", "WEEKLY", "MONTHLY"],
    start_date: Optional[date] = None
):
    """
    Schedule recurring progress check-ins using Google Calendar.
    
    Args:
        frequency: Recurrence frequency (DAILY, WEEKLY, MONTHLY)
        start_date: Start date for the recurring events (optional, defaults to current date)
    
    Returns:
        Google Calendar event details with recurrence rules
    """

    creds = authenticate_google()
    print(creds)
    service = build("calendar", "v3", credentials=creds)
    print("Service", service)
    
    user = ctx.context
    
    # Use current date if no start_date provided
    if start_date is None:
        start_date = date.today()
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = start_datetime + timedelta(minutes=30)
    

    event_info = {
        "summary": f"Progess Check-in for {user.name.title()}",
        "description": "",
        "start": {"dateTime": start_datetime.isoformat(), "timeZone": "UTC" },
        "end": {"dateTime": end_datetime.isoformat(), "timeZone": "UTC" },
        "recurrence": [f"RRULE:FREQ={frequency};COUNT=10"],
    }

    event = service.events().insert(calendarId="primary", body=event_info).execute()
    
    print(event)
    print(dict(event))
    
    
# def main():

#     user = UserSessionContext(name="ABCD", uid="uid-asdfghj-1234567")    
#     context = RunContextWrapper(context=user)
    
#     checkin_scheduler(
#         context,
#         frequency="WEEKLY",
#     start_date=date(year=2025, month=4, day=8)
#     )
    
# main()


