# Carbon Tracker - Full Stack Web Application

A comprehensive web application for tracking individual carbon emissions with real-time dashboards, user management, and IoT data simulation.

## Features

### User Features
- **User Registration & Authentication**: Secure login/register system with email validation
- **Personal Dashboard**: Real-time carbon emission tracking with interactive charts
- **Emission Categories**: Track Travel, Electricity, and Food emissions
- **Carbon Limit Management**: Set and monitor monthly carbon limits
- **Limit Warnings**: Visual alerts when carbon limit is exceeded
- **Real-time Updates**: Dashboard refreshes every 30 seconds

### Admin Features
- **User Management**: View all users and their emission data
- **CSV Data Upload**: Bulk import mock IoT emission data
- **Manual Data Entry**: Add individual emission records for any user
- **System Overview**: Comprehensive statistics and monitoring

### Technical Features
- **Responsive Design**: Mobile-friendly interface with modern UI
- **Interactive Charts**: Bar charts for daily emissions and pie charts for category breakdown
- **SQLite Database**: Lightweight, file-based database
- **Role-based Access Control**: Separate user and admin interfaces
- **Real-time Simulation**: Mock IoT data for testing and demonstration

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Authentication**: Flask-Login with JWT-like sessions

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Clone or Download
```bash
# If using git
git clone <repository-url>
cd Carbon_tracker

# Or download and extract the files
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

### Step 4: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

## Default Login Credentials

### Admin Account
- **Email**: admin@carbon.com
- **Password**: admin123

### Create User Account
1. Click "Register here" on the login page
2. Fill in your details and create an account
3. Set an optional carbon limit during registration

## Usage Guide

### For Regular Users

1. **Login**: Use your registered email and password
2. **Dashboard**: View your monthly emission statistics and charts
3. **Add Entries**: Use the sidebar form to add today's emission data
4. **Update Limit**: Modify your monthly carbon limit as needed
5. **Monitor Progress**: Watch for limit warnings and track your progress

### For Administrators

1. **Admin Panel**: Access the admin panel after login
2. **User Management**: View all registered users and their data
3. **CSV Upload**: 
   - Prepare CSV file with format: `email,date,activity_type,emission_kgco2e,source`
   - Use the upload form to import bulk data
4. **Manual Data Entry**: Add individual emission records for any user
5. **System Monitoring**: Track overall system statistics

## CSV Upload Format

The admin can upload CSV files with the following format:

```csv
email,date,activity_type,emission_kgco2e,source
user@example.com,2024-01-15,Travel,25.5,mock_iot
user@example.com,2024-01-15,Electricity,12.3,mock_iot
user@example.com,2024-01-15,Food,8.7,mock_iot
```

**Required Fields:**
- `email`: User's email address (must exist in system)
- `date`: Date in YYYY-MM-DD format
- `activity_type`: One of Travel, Electricity, or Food
- `emission_kgco2e`: CO2 emissions in kilograms
- `source`: Usually "mock_iot" for uploaded data

## Database Schema

### Users Table
- `id`: Primary key
- `full_name`: User's full name
- `email`: Unique email address
- `password`: Hashed password
- `role`: User role (user/admin)
- `carbon_limit`: Monthly carbon limit (optional)
- `registered_at`: Registration timestamp

### Emissions Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `date`: Emission date
- `activity_type`: Category (Travel/Electricity/Food)
- `emission_kgco2e`: CO2 emissions in kg
- `source`: Data source (manual/mock_iot)
- `created_at`: Record creation timestamp

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### User Dashboard
- `GET /dashboard` - User dashboard page
- `POST /add_emission` - Add emission entry
- `POST /update_limit` - Update carbon limit
- `GET /api/dashboard_data` - JSON data for dashboard

### Admin Panel
- `GET /admin` - Admin panel page
- `POST /admin/upload_csv` - Upload CSV data
- `POST /admin/add_mock_data` - Add manual mock data

## Customization

### Adding New Emission Categories
1. Update the activity type options in templates
2. Modify the database model if needed
3. Update chart colors and labels

### Styling Changes
- Modify CSS in `templates/base.html`
- Update Bootstrap classes in templates
- Customize chart colors and themes

### Database Changes
- Modify models in `app.py`
- Run database migrations if needed
- Update related queries and forms

## Troubleshooting

### Common Issues

1. **Database Errors**
   - Delete `carbon_tracker.db` file and restart
   - Check file permissions in the application directory

2. **Import Errors**
   - Ensure all requirements are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Port Already in Use**
   - Change port in `app.py`: `app.run(debug=True, port=5001)`
   - Or kill existing process using port 5000

4. **CSV Upload Issues**
   - Verify CSV format matches the required structure
   - Check that user emails exist in the system
   - Ensure file is properly encoded (UTF-8)

## Security Notes

- Change the `SECRET_KEY` in production
- Use HTTPS in production environments
- Implement proper password policies
- Add rate limiting for login attempts
- Consider using environment variables for sensitive data

## Future Enhancements

- Email notifications for limit exceedances
- Weekly/monthly report generation
- Dark mode support
- Mobile app integration
- Advanced analytics and predictions
- Social features and challenges
- Integration with real IoT devices

## License

This project is open source and available under the MIT License.

**Happy Carbon Tracking! 🌱** 
