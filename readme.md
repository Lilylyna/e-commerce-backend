E-Commerce Backend

This project is a backend system for an e-commerce website. It manages core functionalities such as user authentication, product management, shopping carts ...ect . The backend is built using Python (Django/RestAPI)

- Features

- User Authentication
  - Handle registration, login, logout, sessions, and JWT tokens (if API). Manage permissions (user vs admin).
- Product Creation (backend only)
- Add to Cart (using session & Database)
- Checkout
  - Create a Wishlist model tied to users; handle API endpoints to add/remove/view wishlisted items.
- Filters and categories (focusing on the backend tho)
- Auto gen.invoice (receipt)
- Admin section
- Dashboard/Stats

- (additional as we will have to look into it)

  - Real payment integration
  - Dashboard/Stats

- Tech Stack

Backend: Python, Django, Django REST Framework

Database: sqlite

Authentication: ....

#####

- Instructions:

## Setup Instructions (in terminal)

1. Clone the Repository
   git clone <your-repository-url>
   cd e-commerce-backend

2. Set Up Virtual Environment (Recommended)
   python -m venv venv
   venv\Scripts\activate

_Note: Virtual environment is optional but recommended to avoid dependency conflicts.
if u wish to use it remember to repeat step 2 in ur project directory everytime u wish to edit/open the project._
$ python -m venv venv $ venv\Scripts\activate

3. Install Dependencies
   pip install django

4. Navigate to Project Directory
   cd ecomprj

5. Set Up Database
   python manage.py makemigrations
   python manage.py migrate

6. Run Development Server
   python manage.py runserver

The server will start at 'http://127.0.0.1:8000/' 7. Test the Setup
Visit 'http://127.0.0.1:8000/' to see the welcome message.
