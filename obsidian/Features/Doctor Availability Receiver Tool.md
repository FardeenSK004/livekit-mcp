# Feature: Doctor Availability Receiver Tool

## Purpose
The `receive_doctor_availability` tool enables the `MantraAssist-backend` client to push calculated doctor schedules, working hours, and bookable time slots directly to the `livekit-mcp` server so the LiveKit Voice Agent can use them naturally during live voice calls.

## Key Arguments
- **`doctor_id`** (int, required): Doctor ID from `users` table.
- **`doctor_name`** (str, required): Full name with title (e.g. `Dr. Ananya Sharma`).
- **`date`** (str, required): Target date (`YYYY-MM-DD`).
- **`timezone`** (str, required): Local timezone string (`Asia/Kolkata`).
- **`available_slots`** (list[str], required): Array of open slots (`["10:00 AM – 11:00 AM", ...]`).
- **`specialization`** (str, optional): Doctor's medical specialty.
- **`booked_slots`** (list[str], optional): Booked appointments on that date.
- **`slot_interval_minutes`** (int, optional, default: 60): Appointment duration in minutes.
- **`notes`** (str, optional): Clinical notes, break hours.

## Contract Reference
See [format.json](file:///home/fardeen/livekit-mcp/format.json) for the full JSON specification.
