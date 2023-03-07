# hotel_database

1. Project dependencies besides the Python default modules are mentioned in the "requirements.txt" file 
2. To open the app we run the "main.py" script

/User as a Client/
  1. If we want to use the app as a client first we register through the interface filling all the necessary fields.
  2. To browse through the available hotel rooms in the next window, we fill in the dates and the number of people in the group and then check the indicative extra benefits
  3. After the results are shown we can choose through multiple scenarios of stay with the dropdown menu by pressing "Προβολή σεναρίου φιλοξενίας".
  4. To make a reservation we use the 
  5. To see the details of current or previous bookings we use the next tab. We can also cancel a booking (but of course not one that has already been checked-in from an admin)

/User as Admin/
  1. To use the app as an admin we use the username and password "georgepetr" and "123456" (clearly indicative. We can also add new admins)
  2. To check-in a group of people we write their reservation number and then choose the specific rooms to place them upon their arrival
  3. In the last tab we can display indicative statistics regarding the hotel, the guests and the reservations


Examples of hotel data, users and admins are contained within .xlsx files in the excel_data folder. 

During development, the main goal was to optimize the room-browsing aspect of the app by combining SQLite queries and different python modules to match the feel of commercial booking applications. Apart from that, the resulting app is very scalable and flexible. The GUI is simple but can easily be modified
