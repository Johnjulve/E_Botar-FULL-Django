# E-Botar - Electronic Voting System

**Version 26.0** | A comprehensive electronic voting system for student government elections

---

## 📖 Core Documentation

Use these six docs for everything you need:
- **[README.md](README.md)** – Overview & Quick Start (this file)
- **[Phase_Implementation.md](Phase_Implementation.md)** – Complete phasing process documentation
- **[guide.md](guide.md)** – All guides, tutorials, and setup instructions
- **[CHANGELOG.md](CHANGELOG.md)** – Comprehensive history of changes and features
- **[MODEL_RELATIONSHIPS_ANALYSIS.md](MODEL_RELATIONSHIPS_ANALYSIS.md)** – Complete model relationship documentation
- **[MODULE_SEPARATION_GUIDE.md](MODULE_SEPARATION_GUIDE.md)** – Module boundaries and separation guide

---

## ✨ Key Features

### 🗳️ **Secure Voting System**
- **Multi-layer Encryption**: Votes encrypted with anonymized receipts
- **Privacy-Preserving**: Anonymous vote tallying with personal ballot verification
- **One-Vote-Per-Position**: Database-level unique constraints prevent duplicate voting
- **Real-Time Results**: Live vote counting with automatic percentage calculations
- **Vote Verification**: Encrypted receipt codes for voter verification

### 👥 **User Management**
- **Google OAuth Integration**: One-click authentication with Google accounts
- **Student Registration**: Complete registration system with email validation
- **Profile Management**: Student ID validation (XXXX-XXXXX format), department/course selection
- **Bulk Operations**: CSV/Excel import and export capabilities
- **User Verification**: Admin-controlled verification system

### 🏛️ **Election Management**
- **Multi-Election Support**: Manage multiple concurrent and sequential elections
- **Precise Scheduling**: Start and end date/time with timezone support
- **Position Management**: Flexible position creation with drag-and-drop reordering
- **Automatic State Transitions**: Time-based election status updates
- **Historical Data**: Complete election history preservation

### 🎯 **Candidate Applications**
- **Application System**: Complete candidate application workflow
- **Availability Control**: Applications only available for upcoming elections
- **Review Process**: Admin-controlled application approval with feedback
- **Party Affiliation**: Support for registered parties and custom party names
- **Manifesto System**: Detailed candidate platform descriptions

### 📊 **Results & Analytics**
- **Real-Time Analytics**: Live vote counting and display
- **Data Visualization**: Chart.js integration for interactive charts
- **Export Capabilities**: CSV/PDF export for results
- **Participation Metrics**: Voter turnout and engagement statistics
- **Historical Trends**: Election result comparisons over time

### 👨‍💼 **Admin Dashboard**
- **Comprehensive Management**: User, election, candidate, and system administration
- **Activity Monitoring**: Real-time system activity display
- **Bulk Operations**: User import/export, password management
- **System Health**: Performance monitoring and error tracking
- **Custom Admin Interface**: Modern, responsive admin panel

### 🔒 **Security Features**
- **Django Authentication**: Robust built-in authentication system
- **CSRF Protection**: Cross-site request forgery prevention
- **Password Security**: PBKDF2 hashing with salt
- **Vote Encryption**: Multi-layer encryption for vote data
- **Activity Logging**: Comprehensive audit trail for all actions
- **Access Control**: Role-based permissions and restrictions

### 📱 **Modern UI/UX**
- **Responsive Design**: Mobile-first approach with Bootstrap 5.3
- **Brand Identity**: University green (#0b6e3b) and yellow (#f4cc5c) theme
- **Accessibility**: WCAG compliance considerations
- **Interactive Elements**: Card-based voting, drag-and-drop admin features
- **Toast Notifications**: User-friendly feedback system

---

## 🛠️ Technology Stack

- **Backend**: Django 4.2+ with modular architecture
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: Bootstrap 5.3 + Custom CSS with CSS variables
- **Authentication**: Django built-in + Google OAuth 2.0
- **Security**: Multi-layer encryption, CSRF protection, activity logging
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome comprehensive icon library

---

## 🏗️ System Architecture

### Modular Design
The system is organized into 7 core modules:

```
E_Botar/
├── auth_module/          # User authentication & profiles
├── voting_module/        # Core voting functionality
├── candidate_module/     # Candidate applications & management
├── election_module/      # Election configuration & management
├── admin_module/         # Administrative functions
├── security_module/      # Security monitoring & logging
├── result_module/        # Results display & analytics
├── E_Botar/             # Project settings & configuration
│   ├── services/        # Consolidated services
│   ├── utils/           # Consolidated utilities
│   └── management/      # Consolidated management commands
├── Template/            # HTML templates organized by module
├── static/              # CSS, JS, images organized by module
└── media/               # User uploads
```

### Key Models
- **User & UserProfile**: Student accounts with academic information
- **SchoolElection**: Election periods with scheduling
- **SchoolPosition**: Available positions (President, VP, etc.)
- **Candidate**: Approved candidates with party affiliation
- **CandidateApplication**: Application workflow and review
- **VoteReceipt**: Privacy-preserving vote receipts
- **EncryptedBallot**: Personal ballot copies for verification
- **AnonVote**: Anonymous vote records for tallying
- **ActivityLog**: Comprehensive audit trail

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

### 1. Navigate to Project
```powershell
cd "D:\Downloads_D\Project Thesis\E_Botar"
```

### 2. Activate Virtual Environment
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Or use the batch file
.\start_server.bat
```

### 3. Install Dependencies (First Time Only)
```powershell
pip install -r requirements.txt
```

### 4. Setup Database (First Time Only)
```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Server
```powershell
python manage.py runserver
```

### 6. Access Application
- **Main Application**: http://127.0.0.1:8000/
- **Custom Admin**: http://127.0.0.1:8000/admin-ui/
- **Django Admin**: http://127.0.0.1:8000/admin/

---

## 📋 Basic Usage

### For Students
1. **Register** → Create account with student details
2. **Complete Profile** → Add Student ID (format: XXXX-XXXXX)
3. **Vote** → Participate in active elections
4. **Apply as Candidate** → Submit application when elections are upcoming
5. **View Results** → Check previous election results

### For Administrators
1. **Create Election** → Set up new election with dates
2. **Add Positions** → Define positions for the election
3. **Review Applications** → Approve/reject candidate applications
4. **Manage Users** → Create, edit, bulk import students
5. **Monitor Activity** → View logs and statistics

**👉 [See Complete User Guide in guide.md](guide.md)**

---

## 🔒 Security Features

### Authentication & Authorization
- ✅ Django authentication & authorization
- ✅ Google OAuth 2.0 integration
- ✅ CSRF protection on all forms
- ✅ Password hashing (PBKDF2)
- ✅ Session management with timeout

### Vote Security
- ✅ Multi-layer vote encryption
- ✅ Anonymous vote tallying
- ✅ Encrypted vote receipts
- ✅ One-vote-per-position enforcement (DB constraint)
- ✅ Personal ballot verification system

### Data Protection
- ✅ SQL injection prevention (ORM-based queries)
- ✅ XSS protection (template auto-escaping)
- ✅ Secure file uploads with validation
- ✅ Activity logging for audit trails
- ✅ Data integrity constraints

**👉 [See Security Details in guide.md](guide.md)**

---

## 📊 Database Schema

### Privacy-Preserving Design
The system implements a privacy-preserving voting architecture:

- **VoteReceipt**: Proves user voted without revealing choices
- **EncryptedBallot**: Personal ballot copy for verification
- **AnonVote**: Anonymous vote records for tallying
- **ActivityLog**: Complete audit trail

### Key Relationships
- Users have profiles with academic information
- Elections contain multiple positions
- Candidates run for specific positions in elections
- Votes are encrypted and anonymized for privacy
- All actions are logged for audit purposes

**👉 [See Database Schema in guide.md](guide.md)**

---

## 🎨 UI/UX Features

### Design System
- **Brand Colors**: University green (#0b6e3b) and yellow (#f4cc5c)
- **Typography**: Inter font with system fallbacks
- **Layout**: Card-based designs with soft shadows
- **Navigation**: Responsive sidebar with mobile offcanvas

### Responsive Design
- **Mobile First**: Optimized for mobile devices
- **Breakpoints**: Tablet (768px+), Desktop (992px+), Large Desktop (1200px+)
- **Touch Friendly**: Large touch targets and intuitive gestures

### Accessibility
- **WCAG Compliance**: Proper semantic HTML and ARIA labels
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: Sufficient contrast ratios
- **Screen Reader**: Compatible with assistive technologies

---

## 🐛 Troubleshooting

### Common Issues

**Server won't start?**
```powershell
# Make sure virtual environment is activated
.\venv\Scripts\Activate.ps1
```

**Cannot apply as candidate?**
- Check if there are upcoming elections (Admin → Create Election with future start date)

**Student ID format error?**
- Use format: XXXX-XXXXX (e.g., 2024-12345)

**Google OAuth not working?**
- Check Google Cloud Console configuration
- Verify redirect URIs match exactly

**👉 [See Full Troubleshooting Guide in guide.md](guide.md)**

---

## 📚 Documentation Structure

### Core Documentation Files
- **[README.md](README.md)** – This overview file
- **[Phase_Implementation.md](Phase_Implementation.md)** – Complete phasing process documentation
- **[guide.md](guide.md)** – All guides, tutorials, and detailed instructions
- **[CHANGELOG.md](CHANGELOG.md)** – Comprehensive change history
- **[MODEL_RELATIONSHIPS_ANALYSIS.md](MODEL_RELATIONSHIPS_ANALYSIS.md)** – Complete model relationship documentation
- **[MODULE_SEPARATION_GUIDE.md](MODULE_SEPARATION_GUIDE.md)** – Module separation and architecture guide

### Tutorial Contents
- **Setup Guide**: Installation and configuration
- **User Guides**: Student and administrator workflows
- **Technical Documentation**: System architecture and API reference
- **Security Features**: Detailed security implementation
- **Database Schema**: Complete database design
- **Troubleshooting**: Common issues and solutions

---

## 📊 Version History

### Current Version: v20.0 (Breakthrough)
- Complete system restructuring with modular architecture
- Google OAuth integration
- Enhanced security with privacy-preserving voting
- Modern UI/UX with responsive design
- Comprehensive documentation

### Recent Versions
- **v17.0**: CSS restructuring with component-based organization
- **v16.0**: Template implementation with 32 organized templates
- **v15.0**: Student ID format validation (XXXX-XXXXX)
- **v14.0**: Google OAuth integration
- **v13.2**: Candidate section redesign

**👉 [See Complete Version History in Changelog.md](Changelog.md)**

---

## 🎯 Future Roadmap

### Planned Features
- **Mobile App**: Native mobile application development
- **Advanced Analytics**: Enhanced reporting and statistics
- **Real-time Updates**: WebSocket integration for live results
- **API Development**: REST API for third-party integrations

### Technical Enhancements
- **PostgreSQL Migration**: Production database upgrade
- **Redis Integration**: Caching and session management
- **Docker Deployment**: Containerized deployment
- **CI/CD Pipeline**: Automated testing and deployment

---

## 📝 License

This system is proprietary software developed for educational institution use as part of a thesis research project.

---

## 💡 Support

For questions or issues:
1. **Read the documentation** - [guide.md](guide.md)
2. **Check troubleshooting** - Common issues and solutions
3. **Review activity logs** - Admin panel for system events
4. **Contact system administrator** - For technical support

---

## 🙏 Acknowledgments

- **Django Framework** - Python web framework
- **Bootstrap 5** - Responsive CSS framework
- **Font Awesome** - Icon library
- **Chart.js** - Data visualization
- **Google OAuth** - Authentication service
- **Thesis advisors** - Guidance and support

---

## 📞 Quick Links

- 📖 **[Complete Tutorial](guide.md)**
- 🏗️ **[Phase Implementation](Phase_Implementation.md)**
- 🐛 **[Troubleshooting](guide.md#troubleshooting)**
- 🔒 **[Security Features](guide.md#security-features)**
- 📊 **[Database Schema](guide.md#database-schema)**
- 📋 **[Changelog](Changelog.md)**

---

**E-Botar v26.0** | Last Updated: November 11, 2025  
**Status**: Production Ready | **Architecture**: Modular Design