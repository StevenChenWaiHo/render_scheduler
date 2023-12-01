import argparse
import json
from datetime import datetime, timedelta

def parseDateString(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')

def toDateString(date):
    return date.strftime('%Y-%m-%dT%H:%M:%SZ')

def preprocessor(schedule_file, overrides_file, start_date_str, end_date_str):
    """
    Parse the file path and date string

    Aruguments:
    - schedule_file {String} --File path to the schedule JSON file
    - overrides_file {String} --File path to the overrides JSON file
    - start_date_str {String} --Date string of start date
    - end_date_str {String} --Date string of end date

    Returns:
    - schedule {Dictionary} --Dictionary about the schedule
    - overrides {[Dictionary]} -- Array of dictionary about the overrides
    - start_date {Datetime} --Datetime object of start date
    - end_date {Datetime} --Datetime object of end date
    """ 
    schedule_file_stream = open(schedule_file)
    overrides_file_stream = open(overrides_file)

    # Extract JSON file
    schedule = json.load(schedule_file_stream)
    overrides = json.load(overrides_file_stream)

    # String to Datetime object
    start_date = parseDateString(start_date_str)
    end_date = parseDateString(end_date_str)


    return schedule, overrides, start_date, end_date

def render_schedule(schedule, overrides, start_date, end_date):
    """
    Render schedule between start_date and end_date after overrides if overrides exist.

    Aruguments:
    - schedule {Dictionary} -- Dictionary about the schedule
    - overrides {[Dictionary]} -- Array of dictionary about the overrides
    - start_date {Datetime} -- Datetime object of start date
    - end_date {Datetime} -- Datetime object of end date

    Returns:
    - {[Dictionary]} The (overrided) schedule between start_date and end_date in Dictionary array.
    """ 

    # Get the schedule between start_date and end_date without overrides
    all_schedule = schedule_between_dates(schedule, start_date, end_date)

    # print(f'Before Override: {all_schedule}')
    # Override the schedule if overrides exist
    if (overrides):
        overrided_schedule = overrides_schedule(all_schedule, overrides)

    # print(f'After Override: {overrided_schedule}')
    return overrided_schedule


def schedule_between_dates(schedule_data, start_date, end_date):
    """
    Render schedule between start_date and end_date.

    Aruguments:
    - schedule_data {Dictionary} --Dictionary about the schedule
    - start_date {Datetime} --Datetime object of start date
    - end_date {Datetime} --Datetime object of end date

    Returns:
    - {[Dictionary]} The schedule between start_date and end_date in Dictionary array.
    """ 
    
    users = schedule_data['users']
    schedule_start_date_str = schedule_data['handover_start_at']
    interval_days = schedule_data['handover_interval_days']

    schedule_start_date = parseDateString(schedule_start_date_str)

    shift_arr = []
    user = 0
    shift_start = schedule_start_date
    shift_end = schedule_start_date + timedelta(days=interval_days)
    
    def nextShift():
        nonlocal shift_start, shift_end, user, users, interval_days
        shift_start = shift_end
        shift_end = shift_start + timedelta(days=interval_days)
        user = (user + 1) % len(users)
    
    # Step until user shift end date is after start date
    while (shift_end <= start_date):
        nextShift()
    
    # Add the first shift
    start_date = max(start_date, schedule_start_date) # start_date might be before schedule_start_date
    shift_arr.append({"user": users[user], "start_at": toDateString(start_date), "end_at": toDateString(shift_end)})
    nextShift()


    # Start iterating until end_date
    while (shift_start < end_date):

        if (shift_end >= end_date):
            shift_end = end_date

        shift_arr.append({"user": users[user], "start_at": toDateString(shift_start), "end_at": toDateString(shift_end)})
        nextShift()

    return shift_arr

def overrides_schedule(schedule, overrides):
    """
    Override schedule with overrides.

    Aruguments:
    - schedule {[Dictionary]} -- Array of dictionary about the schedule
    - overrides {[Dictionary]} -- Array of dictionary about the overrides

    Returns:
    - {[Dictionary]} The (overrided) schedule between start_date and end_date in Dictionary array.
    """ 

    if (len(schedule) <= 0):
        return schedule


    for override in overrides:
        overrided_schedule = []
        # print(f"Override {overrides}")
        override_user = override['user']
        override_start = override['start_at']
        override_end = override['end_at']
        schedule_start_date = schedule[0]['start_at']
        schedule_end_date = schedule[-1]['end_at']

        # Ignore override shift doesn't lie between schedule start date and end date
        if (override_end < schedule_start_date or override_start > schedule_end_date):
            continue

        override_start = max(override_start,schedule_start_date) # Overrided shift start date might be before schedule start date
        override_end = min(override_end, schedule_end_date) # Overrided shift end date might be after schedule end date

        shift = 0
        # Copy schedule until override start date lies between a shift
        while (shift < len(schedule)):
            
            if (override_start >= schedule[shift]['start_at'] and override_start <= schedule[shift]['end_at']):
                # Add overrided shift
                if (schedule[shift]['user'] == override_user): 
                    # Merge start date if previous user is the same as the override user
                    override_start = schedule[shift]['start_at']

                if (override_start != schedule[shift]['start_at']): 
                    # Ignore shift with overlapped start_date
                    overrided_schedule.append({"user": schedule[shift]['user'], "start_at": schedule[shift]['start_at'], "end_at": override_start})
                        
                overrided_schedule.append({"user": override_user, "start_at": override_start, "end_at": override_end})
                break

            overrided_schedule.append(schedule[shift])
            shift += 1

        

        # Find the end of the overrided shift, stop when end date of the override is in between a shift
        while (shift < len(schedule)):

            # Stop when end date of the override is in between a shift
            if (override_end >= schedule[shift]['start_at'] and override_end < schedule[shift]['end_at']):
                # Add overrided shift
                if (schedule[shift]['user'] == override_user): 
                    # Merge end date if next user is the same as the override user
                    override_end = schedule[shift]['end_at']
                    overrided_schedule.pop()
                    overrided_schedule.append({"user": override_user, "start_at": override_start, "end_at": override_end})
                else:
                    overrided_schedule.append({"user": schedule[shift]['user'], "start_at": override_end, "end_at": schedule[shift]['end_at']})
                shift += 1
                break
            shift += 1

        # Copy Rest of the schedule
        while (shift < len(schedule)):
            # Otherwise copy the shift to the new schedule
            overrided_schedule.append(schedule[shift])
            shift += 1
        
        schedule = overrided_schedule

    return overrided_schedule

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Render a schedule')

    # Define arguments
    parser.add_argument('--schedule_', type=str, help='Path to schedule JSON file')
    parser.add_argument('--overrides_', type=str, help='Path to overrides JSON file')
    parser.add_argument('--from_', type=str, help='Schedule Start date and time')
    parser.add_argument('--until_', type=str, help='Schedule End date and time')

    # Parse the command line arguments
    args = parser.parse_args()

    print(f"Schedule File: {args.schedule_}")
    print(f"Overrides File: {args.overrides_}")
    print(f"Start Date: {args.from_}")
    print(f"End Date: {args.until_}")

    schedule, overrides, start_date, end_date = preprocessor(schedule_file=args.schedule_, overrides_file=args.overrides_, start_date_str=args.from_, end_date_str=args.until_)

    print(render_schedule(schedule, overrides, start_date, end_date))