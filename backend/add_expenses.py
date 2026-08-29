from database import get_connection


connection = get_connection()
cursor = connection.cursor()


expenses = [

    ("UP 53 NC 0007", "NH24", "College", "Railway Station", 25, "2026-08-24"),
    ("UP 53 NC 0001", "NH24", "Railway Station", "College", 25, "2026-08-24"),
    ("UP 53 NC 7861", "NH28", "College", "Railway Station", 30, "2026-08-25"),
    ("UP 53 NC 9999", "NH28", "Railway Station", "College", 30, "2026-08-25"),
    ("UP 53 NC 1111", "NH91", "College", "Railway Station", 20, "2026-08-26"),
    ("UP 53 NC 0009", "NH91", "Railway Station", "College", 20, "2026-08-26"),

    ("UP 53 NC 0007", "NH24", "College", "Railway Station", 25, "2026-08-27"),
    ("UP 53 NC 0001", "NH24", "Railway Station", "College", 25, "2026-08-27"),
    ("UP 53 NC 7861", "NH28", "College", "Railway Station", 30, "2026-08-28"),
    ("UP 53 NC 1111", "NH91", "College", "Railway Station", 20, "2026-08-28")

]


for expense in expenses:

    cursor.execute("""
        INSERT INTO bus_expenses
        (
            bus_number,
            route_number,
            start_point,
            end_point,
            fare,
            travel_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, expense)


connection.commit()

connection.close()


print("Bus expense data added successfully.")