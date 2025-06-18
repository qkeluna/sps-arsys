# SPS Appointment System - A Simplified Cal.com Alternative

A modern, simplified SaaS appointment booking system built specifically for photo studios, but easily adaptable for any appointment-based business.

## 🌟 Features

### Core Features

- **Multi-tenant SaaS Architecture**: Each studio gets their own dedicated space
- **Service Packages/Event Types**: Cal.com-style service offerings with custom pricing and durations
- **Public Booking Pages**: Clean, branded booking pages for customers (`/book/studio-slug`)
- **Studio Management**: Complete studio profile and settings management
- **Time Slot Management**: Flexible scheduling with availability controls
- **Appointment Management**: Full lifecycle from booking to completion
- **Email Notifications**: Automated booking confirmations and reminders using Resend
- **User Roles**: Customer, Studio Owner, Staff, and Admin roles

### Event Types/Packages (Cal.com Style)

Like Cal.com's Event Types, our system uses **Service Packages** to define different booking options:

- **Portrait Session** (1 hour, $150)
- **Family Package** (2 hours, $300)
- **Professional Headshots** (30 min, $100)
- **Creative Session** (3 hours, $450)
- **Product Photography** (2 hours, $200)

Each package includes:

- ✅ **Custom Duration**: Fixed, minimum/maximum, or flexible timing
- ✅ **Pricing Control**: Base price with optional equipment add-ons
- ✅ **Buffer Times**: Setup/cleanup time before and after sessions
- ✅ **Availability Rules**: Booking windows, notice requirements, daily limits
- ✅ **Custom Questions**: Collect specific information per package type
- ✅ **Equipment Requirements**: Include or offer optional equipment
- ✅ **Visual Branding**: Featured images and custom colors
- ✅ **Approval Workflow**: Manual approval for special packages

### Technical Features

- **Backend**: FastAPI with PostgreSQL and SQLAlchemy
- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS
- **Authentication**: JWT-based with role-based access control
- **Database**: PostgreSQL with UUID primary keys
- **Email Service**: Resend integration with beautiful HTML templates
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│                 │    │                 │    │                 │
│ - Dashboard     │    │ - Auth API      │    │ - Users         │
│ - Booking Pages │    │ - Studios API   │    │ - Studios       │
│ - Management    │    │ - Packages API  │    │ - Packages      │
│ - Package Setup │    │ - Bookings API  │    │ - Appointments  │
└─────────────────┘    │ - Public API    │    │ - Time Slots    │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Email Service │
                       │   (Resend)      │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.8+
- PostgreSQL (provided via LeapCell)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd sps-arsys
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy environment variables
cp env.example .env

# Edit .env file with your settings:
# - Add your Resend API key
# - Database is already configured
# - Generate a strong SECRET_KEY

# Start the FastAPI server
python start.py
```

The backend will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 3. Frontend Setup

```bash
# Navigate back to root and install dependencies
cd ..
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📁 Project Structure

```
sps-arsys/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── main.py            # FastAPI application
│   │   ├── routers/           # API route handlers
│   │   │   ├── auth.py        # Authentication routes
│   │   │   ├── studios.py     # Studio management
│   │   │   ├── packages.py    # Package/Event Type management
│   │   │   ├── appointments.py # Appointment management
│   │   │   └── public.py      # Public booking API
│   │   └── services/          # Business logic
│   │       ├── auth.py        # Authentication service
│   │       └── email.py       # Email service
│   ├── requirements.txt       # Python dependencies
│   ├── env.example           # Environment variables template
│   └── start.py              # Startup script
├── src/                       # Next.js Frontend
│   ├── app/                   # App Router
│   ├── components/            # React components
│   ├── lib/                   # Utilities and API client
│   ├── hooks/                 # Custom React hooks
│   ├── stores/                # Zustand state management
│   └── types/                 # TypeScript type definitions
└── README.md                  # This file
```

## 🔐 Authentication & User Roles

### User Roles

1. **Customer**: Can book appointments and manage their bookings
2. **Studio Owner**: Can create and manage studios, packages, time slots, and appointments
3. **Staff**: Can manage appointments for assigned studios (future feature)
4. **Admin**: Full system access (future feature)

### Registration Flow

1. Users register as "Customer" by default
2. Customers can promote themselves to "Studio Owner"
3. Studio owners can create and manage studios

## 🎯 Package/Event Type Management

### Creating Service Packages

Studio owners can create unlimited service packages, each with:

```javascript
// Example package configuration
const photographyPackage = {
  name: "Professional Headshots",
  slug: "professional-headshots",
  session_type: "professional",
  duration_minutes: 60,
  base_price: 150.0,
  buffer_time_before: 15, // Setup time
  buffer_time_after: 15, // Cleanup time
  min_booking_notice_hours: 24,
  max_booking_days_ahead: 30,
  custom_questions: [
    {
      id: "wardrobe",
      question: "How many outfit changes?",
      type: "select",
      required: true,
      options: ["1", "2", "3", "4+"],
    },
    {
      id: "usage",
      question: "Intended usage for photos?",
      type: "checkbox",
      options: ["LinkedIn", "Website", "Marketing", "Personal"],
    },
  ],
  included_equipment: ["Professional lighting", "Backdrop", "Retouching"],
  optional_equipment: ["Hair & makeup", "Wardrobe styling"],
  is_public: true,
  requires_approval: false,
};
```

### Package Features

- **Flexible Duration**: Set fixed times or allow customer customization
- **Dynamic Pricing**: Override pricing per time slot if needed
- **Custom Forms**: Collect specific information for each package type
- **Equipment Management**: Define what's included vs. optional
- **Booking Rules**: Control availability and approval requirements
- **Visual Branding**: Add featured images and custom colors

### Public Booking Flow

1. **Package Selection**: Customer browses available packages
2. **Custom Questions**: Fills out package-specific form
3. **Time Selection**: Chooses from available slots
4. **Duration Choice**: Selects duration (if customizable)
5. **Equipment Add-ons**: Selects optional equipment
6. **Confirmation**: Receives immediate booking confirmation

## 🏢 Studio Management

### Creating a Studio

```javascript
// Example API call
const studioData = {
  name: "My Photo Studio",
  slug: "my-photo-studio", // Used for public URLs
  description: "Professional photo sessions",
  email: "hello@myphotostudio.com",
  phone: "+1234567890",
  // ... other details
};

const studio = await apiClient.createStudio(studioData);
```

### Public Booking URL

Each studio gets a public booking page:

```
https://yourdomain.com/book/my-photo-studio
```

## 📅 Time Slot & Appointment Management

### Time Slots

Studio owners create available time slots with:

- Date and time range
- Maximum capacity (multiple bookings per slot)
- Package-specific or general availability
- Price overrides for special dates
- Availability status

### Package-Specific Slots

Time slots can be:

- **General**: Available for any package
- **Package-Specific**: Only bookable for certain packages

### Appointments

Customers can book appointments by selecting:

- Service package (with all its configurations)
- Available time slot
- Custom duration (if allowed)
- Equipment add-ons
- Answering custom questions

## 📧 Email Notifications

The system automatically sends emails for:

- **Booking Confirmations**: Sent immediately after booking
- **Reminders**: 24 hours before appointment (configurable)
- **Cancellations**: When appointments are cancelled
- **Studio Notifications**: New bookings notify studio owners

### Email Templates

Beautiful, responsive HTML email templates include:

- Booking details with package information
- Studio information and location
- Customer responses to custom questions
- Equipment included and add-ons
- Action buttons (reschedule, cancel)

## 🛠️ API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user
- `POST /auth/promote-to-studio-owner` - Upgrade to studio owner

### Studios (Protected)

- `GET /studios/my-studios` - Get user's studios
- `POST /studios/` - Create new studio
- `GET /studios/{studio_id}` - Get studio details
- `PUT /studios/{studio_id}` - Update studio

### Packages/Event Types (Protected)

- `GET /packages/studio/{studio_id}` - Get studio packages
- `POST /packages/` - Create new package
- `GET /packages/{package_id}` - Get package details
- `PUT /packages/{package_id}` - Update package
- `DELETE /packages/{package_id}` - Delete package
- `POST /packages/{package_id}/duplicate` - Duplicate package

### Public API

- `GET /public/studios/{slug}` - Get studio by slug
- `GET /public/studios/{slug}/packages` - Get available packages
- `GET /public/studios/{studio_id}/available-slots` - Get available time slots
- `POST /public/bookings` - Create public booking
- `GET /public/bookings/{booking_id}` - Get booking details
- `POST /public/bookings/{booking_id}/cancel` - Cancel booking

## 🚀 Deployment

### Backend Deployment

1. Set up a server (VPS, Railway, Render, etc.)
2. Install Python and dependencies
3. Set production environment variables
4. Run with a production WSGI server like Gunicorn

### Frontend Deployment

1. Deploy to Vercel, Netlify, or similar
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Build and deploy

### Database

Your PostgreSQL database is already set up on LeapCell:

```
Host: 9qasp5v56q8ckkf5dc.leapcellpool.com
Port: 6438
Database: ofwriuydshinwblrcymk
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```env
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
RESEND_API_KEY=your-resend-key
FROM_EMAIL=noreply@yourdomain.com
FRONTEND_URL=http://localhost:3000
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

## 📈 Future Enhancements

### Phase 2 Features

- [ ] Payment integration (Stripe)
- [ ] Calendar integrations (Google Calendar, Outlook)
- [ ] SMS notifications
- [ ] Advanced scheduling (recurring appointments)
- [ ] Staff management with role assignments
- [ ] Analytics dashboard with booking insights
- [ ] Mobile app for studio owners

### Phase 3 Features

- [ ] Multi-language support
- [ ] Advanced package customization
- [ ] Webhook integrations
- [ ] API rate limiting
- [ ] Advanced reporting and analytics
- [ ] White-label solutions

## 🆚 Comparison with Cal.com

| Feature              | Cal.com | Our System  | Notes                                |
| -------------------- | ------- | ----------- | ------------------------------------ |
| Event Types          | ✅      | ✅          | Called "Packages" in our system      |
| Custom Questions     | ✅      | ✅          | Package-specific forms               |
| Buffer Times         | ✅      | ✅          | Setup/cleanup time                   |
| Pricing              | Basic   | ✅ Advanced | Equipment add-ons, slot overrides    |
| Multi-tenant         | ❌      | ✅          | Each studio is isolated              |
| Equipment Management | ❌      | ✅          | Photo studio specific                |
| Visual Branding      | Limited | ✅          | Custom colors, images per package    |
| Approval Workflow    | ✅      | ✅          | Manual approval for special packages |

## 💡 Cal.com-Style Workflow

### Studio Owner Experience

1. **Create Studio** → Set up studio profile and settings
2. **Design Packages** → Create Event Types (Portrait, Family, etc.)
3. **Set Availability** → Create time slots with capacity
4. **Custom Branding** → Add colors, images, custom questions
5. **Go Live** → Share public booking URL

### Customer Experience

1. **Browse Packages** → See available Event Types
2. **Select Service** → Choose package with pricing/duration
3. **Answer Questions** → Fill custom form for that package
4. **Pick Time** → Select from available slots
5. **Customize** → Adjust duration, add equipment
6. **Book** → Instant confirmation with details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, email support@yourdomain.com or create an issue in this repository.

## 🙏 Acknowledgments

- Inspired by Cal.com's simplicity and effectiveness
- Built with modern, battle-tested technologies
- Designed for scalability and maintainability

---

**Happy Booking! 📸✨**
