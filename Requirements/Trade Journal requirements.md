Requirements:

Create a Trading Journal App in python.  Enable Importing trade execution data in .CSV format.(see below for the format of this data)  Store trade data and other app data in the best format for this task (e.g. flat file, .csv file, database). whatever you decide.

Here are the UI tab and feature/function requirements: 

## (A) Daily Debrief tab

Create a tab that end user can use to describe in Text the following 3 steps in the Debrief process for each day:

1) Debrief  
   1) Intra day summary  
   2) Feelings/self-talk

2) Recurring patterns  
   1) When they best play out

3) Using this information to leverage up/down

- Enable viewing the 3 steps for a specific day  
- Automatically re-initialize these fields to empty on a new trading day, starting at 3pm each day, Sunday-Friday.

## (B) Import trade data

Provide a means to import trade data in .csv format.  Here is the format:

See file: trade\_data\_format.png

## (C) Fields & Data tab

Display trades in a tab like this list below.  Add a “Filters” feature to enable the User to filter the display of trades based on one or more fields.

See file: fields\_and\_data\_tab.png

1) Show trades in a list like this image  
2) Exclude “Stop Price”  
3) Exclude “High Price” and “Low Price”  
4) Add the field MAE and MFE to this list  
5) Add the field “Bars” to this list  
6) the “Entry Strategy” and “Photo” fields are selection boxes:  
   \- Entry Strategy field: should include the following items: balance-VAH, balance-VAL, p-POC, p-VWAP, b-POC, b-VWAP, PoorHigh, PoorLow

   \- Photo field: brings up a “Choose files” window

7) The “Photo” field should be capable of saving multiple files at once \- screenshots/images  
8) Add the ability to select filters (including ‘None’) to apply to this list including:  
   1) View trades by day, week, month  
   2) View trades by all fields except ‘Multiplier’, Commission  
   3) View trades by time range (e.g. all trades between 6:30am and 9am)  
   4) View trades by bar range (e.g. all trades active for 5-10 bars)

9) The ‘Multiplier’ field is based on a User-defined setting defined for each Instrument that is present in the Fields/data list.  This ‘Multiplier’ value is set by end user for each Instrument.

10) Here is an idea of multiplier values for different instruments.

See file: multiplier\_info.png

## (C) Statistics tab

Display the following Statistics on the Statistics tab.  The “Start Date” and “End Date” fields are set by the End user.  Calculate these statistics from the information currently filtered and displayed in the “Fields & Data” tab.  Provide a Refresh button to refresh the Statistics based on the “Fields & Data” tab.

See file: statistics\_tab.png

