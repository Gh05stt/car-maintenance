import json
import smtplib
from datetime import date, timedelta

filename = 'data.json'
keys = 'keys.json' #app key

def load_keys(keys):
    with open(keys, 'r') as f:
        data = json.load(f)

    return data

# Save to JSON file 
def save(values, filename):
    try:
        # Load data
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        #if file empty, make a list
        data = []

    # Append new values
    data.append(values)
    
    # Save updated data back to the file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4) 

# Load JSON file values
def load(filename):
    with open(filename, 'r') as f:
        read = json.load(f) 
    return read

# Get user input
def get_service():
    # Get date
    d = date.today()
    service = input("Service done to the car: ")

    # Get time till next service
    while True:
        next_service = input("Months until next service: ")
        if next_service.isdigit():
            next_service = int(next_service)
            break

        print("Invalid Input!")

    return [d.isoformat(), service, next_service]  # Convert date to ISO format and include next_service

#Sends email to user
def send_email():

    k = load_keys(keys)
    
    sender = k[1][1] #Email that sends
    receiver = k[2][1] #Email that receives

    #Content of the email
    subject = "Car Service Reminder"
    message = get_email_content(filename)

    text = f"Subject: {subject} \n\n {message}"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(sender, k[0][1])

    server.sendmail(sender, receiver, text)

    print("Email Sent!")


def get_email_content(filename):
    data = load(filename)
    today = date.today()
    upcoming_services = []

    for item in data:
        last_service_date = date.fromisoformat(item[0])
        service = item[1]
        months_until_next_service = item[2]

        # Calculate the next service date
        year = last_service_date.year
        month = last_service_date.month + months_until_next_service
        day = last_service_date.day

        # Handle year rollover
        while month > 12:
            month -= 12
            year += 1

        try:
            next_service_date = date(year, month, day)
        except ValueError:
            if month == 2:  # February
                if day > 28:
                    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):  # Leap year
                        day = 29
                    else:
                        day = 28
            else:
                while True:
                    try:
                        next_service_date = date(year, month, day)
                        break
                    except ValueError:
                        day -= 1

        days_until_next_service = (next_service_date - today).days

        if days_until_next_service <= 14:  # Check if the service is due within 14 days
            upcoming_services.append(f"Your next {service} is due in {days_until_next_service} days.")
        else:
            return "No services"
    return "\n".join(upcoming_services)



if __name__ == "__main__":
    # Get email content for upcoming services
    email_content = get_email_content(filename)

    # Check if there are upcoming services
    if "No services" in email_content:
        print(email_content)
        print("Please log a new service.")
        service_data = get_service()
        save(service_data, filename)
    else:
        # Send email if there are upcoming services
        send_email()
