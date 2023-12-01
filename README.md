# Render Schedule

This script implements a scheduling algorithm for an on-call system. It takes a schedule configuration and override information to output a final schedule within a specified time range.

# Requirements
- Python 3.8.10

# Usage
## Bash (Unix)
Make sure you are in the same directory with the script file
```
./render-schedule --schedule <path_to_schedule_file> --overrides <path_to_overrides_file> --from <from_time> --until <until_time>
```

## Python (Others)
Make sure you are in the same directory with the python file
```
python3 ./render-schedule,py --schedule <path_to_schedule_file> --overrides <path_to_overrides_file> --from <from_time> --until <until_time>
```


## Arguements
Arguments:
- schedule: Path to a JSON file containing the definition of the schedule.
- overrides: Path to a JSON file containing an array of overrides.
- from_time: Start time of the schedule (format: 'YYYY-MM-DDTHH:mm:ssZ').
- until_time: End time of the schedule (format: 'YYYY-MM-DDTHH:mm:ssZ').

## Sample
schedule.json
```
// This is a schedule.
{
  "users": [
    "alice",
    "bob",
    "charlie"
  ],

  // 5pm, Friday 17th November 2023
  "handover_start_at": "2023-11-17T17:00:00Z",
  "handover_interval_days": 7
}
```
overrides.json
```
// This is an override array.
[{
  // Charlie will cover this shift
  "user": "charlie",
  // 5pm, Monday 20th November 2023
  "start_at": "2023-11-20T17:00:00Z",
  // 10pm, Monday 20th November 2023
  "end_at": "2023-11-20T22:00:00Z"
}]
```

# Run Test
All test cases are in the `tests` folder.

## Bash (Unix)
You can run all the tests by using the test-all script
```
./test-all
```

## Python (Others)
You can run all the tests by python3
```
python3 ./test_all.py
```