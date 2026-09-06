# Expense Claims

A role-based expense claim management application that helps employees submit expenses, managers review and approve claims, and finance track payments and monthly spending.

## Live Demo

**Application:** https://expense-claims-8heb.onrender.com

> Registration is not enabled in this demo. Please use the pre-created demo accounts below.

## Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| Employee | employee@expenseapp.com | Employee@123 |
| Manager | manager@expenseapp.com | Manager@123 |
| Finance | finance@expenseapp.com | Finance@123 |

These accounts are provided specifically for testing the application.

---

## Features

### Employee

- Create expense claims
- Enter expense details manually
- Paste receipt text and extract claim information using AI
- Review and edit AI-extracted information before submission
- Upload receipt images
- View submitted claims and their current status
- Detect possible duplicate claims

### Manager

- View claims submitted by their team
- Review claim details
- Approve or reject employee claims
- Submit their own expense claims
- Prevent managers from approving their own claims

### Finance

- View approved claims
- Mark approved claims as paid
- Track payment status
- View monthly spending
- View spending by employee and category
- Compare employee spending against monthly limits
- Identify employees who have exceeded their monthly limit

---

## Claim Workflow

The main claim lifecycle is:

    PENDING
       |
       +------> APPROVED ------> PAID
       |
       +------> REJECTED

A paid claim is considered final and cannot move back to another status.

---

## Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** PostgreSQL through Supabase
- **Authentication:** Supabase Auth
- **File Storage:** Supabase Storage
- **AI:** Google Gemini API
- **Deployment:** Render
- **Version Control:** Git and GitHub

---

## Project Structure

    expense-claims/
    │
    ├── app.py
    ├── config.py
    ├── requirements.txt
    ├── README.md
    │
    ├── database/
    │   ├── schema.sql
    │   └── seed.sql
    │
    ├── routes/
    │   ├── auth_routes.py
    │   ├── claim_routes.py
    │   ├── dashboard_routes.py
    │   ├── finance_routes.py
    │   └── manager_routes.py
    │
    ├── services/
    │   ├── ai_service.py
    │   ├── analytics_service.py
    │   ├── duplicate_service.py
    │   ├── receipt_service.py
    │   └── supabase_service.py
    │
    ├── utils/
    │   ├── auth.py
    │   ├── permissions.py
    │   └── validators.py
    │
    ├── templates/
    └── static/

---

## How to Run Locally

### 1. Clone the repository

    git clone https://github.com/vkrvkr763-lgtm/expense-claims.git

    cd expense-claims

### 2. Create a virtual environment

    python3 -m venv venv

Activate it:

Linux/macOS:

    source venv/bin/activate

Windows:

    venv\Scripts\activate

### 3. Install dependencies

    pip install -r requirements.txt

### 4. Configure environment variables

Create a `.env` file in the project root:

    SUPABASE_URL=your_supabase_url
    SUPABASE_KEY=your_supabase_key
    SECRET_KEY=your_flask_secret_key
    GEMINI_API_KEY=your_gemini_api_key

Do not commit `.env` or any API keys to GitHub.

### 5. Run the application

    python app.py

The application will be available at:

    http://127.0.0.1:5000

---

## Database Setup

The database schema is provided in:

    database/schema.sql

Sample/demo data is provided in:

    database/seed.sql

The application uses Supabase PostgreSQL for storing:

- User profiles
- Expense claims
- Claim status history
- Monthly limits
- Approval and payment information

Supabase Storage is used for receipt images.

---

## AI Receipt Extraction

Google Gemini is used to reduce manual data entry.

The user can paste receipt text into the claim form. The application sends the receipt text to Gemini and asks it to extract structured information such as:

- Amount
- Expense date
- Merchant
- Category
- Description

The extracted information is then shown back to the user before the claim is submitted.

The user can modify any AI-generated value before submitting the claim.

### Why this approach?

AI is treated as an assistant rather than the source of truth. Receipt information can be messy or ambiguous, so the user always gets the opportunity to review and correct the extracted values.

---

## Duplicate Detection

The application checks newly submitted claims against previous claims from the same user.

The duplicate score considers factors such as:

- Exact or similar amount
- Merchant similarity
- Description similarity
- Same expense date

A high similarity score produces a **Possible Duplicate** warning.

The claim is not automatically deleted or rejected. Instead, it is flagged so that the manager/finance team can review it.

This handles cases where the same receipt is submitted twice with slightly different wording.

---

## Roles and Permissions

### Employee

Employees can:

- Create claims
- View their own claims
- Track claim status

### Manager

Managers can:

- View claims from their team
- Approve or reject team claims
- Create their own claims

A manager cannot approve their own claim.

### Finance

Finance can:

- View approved claims
- Mark claims as paid
- View monthly spending and limits

Role-based access is enforced in the application so users cannot access functionality intended for another role.

---

## Claim Status Rules

The application uses the following status rules:

- `PENDING` → `APPROVED`
- `PENDING` → `REJECTED`
- `APPROVED` → `PAID`

Once a claim is `PAID`, it is treated as a final state and cannot move backwards.

Rejected claims are also treated as final.

These rules are enforced at the database level as well as in the application workflow.

---

## Decisions and Assumptions

The task did not specify every detail of the business workflow, so the following decisions were made:

### 1. Registration

Registration is not included in this demo.

Three pre-created accounts are provided for testing so reviewers can directly test each role.

### 2. Payment

Actual payment gateway integration is not required. Finance marking a claim as **Paid** represents the payment step.

### 3. Duplicate Claims

A duplicate is treated as a warning rather than automatically blocking the claim.

This allows legitimate repeated expenses to still be submitted while giving reviewers a signal that the claim may need investigation.

### 4. Monthly Limits

Each applicable user has a configured monthly spending limit.

Finance analytics compares monthly spending against that limit and highlights users who have exceeded it.

### 5. Manager Approval

A manager can approve claims belonging to their team but cannot approve their own claim.

### 6. AI Extraction

AI-generated claim information is treated as a suggestion. The user must review the extracted information and can correct it before submission.

### 7. Receipt Images

Receipt images can be uploaded and stored with the claim. The current AI extraction flow primarily uses pasted receipt text for structured extraction.

---

## Sample Data

The application includes realistic expense examples such as:

- Meals
- Travel
- Taxi
- Supplies

The demo data also includes:

- Poorly formatted receipt text
- Similar/differently worded duplicate receipts
- Users approaching their monthly spending limits

This was done to represent realistic business scenarios rather than only simple test records.

---

## What I Would Improve With Another Week

If I had another week, I would focus on the following:

### 1. Image-based AI extraction

Extend the AI workflow so uploaded receipt images can also be sent directly to a vision-capable model for OCR and structured extraction.

### 2. Better duplicate detection

Improve duplicate detection using stronger semantic similarity and receipt-level identifiers where available.

### 3. Manager approval hierarchy

Introduce a configurable approval hierarchy so manager claims can be routed to a higher-level approver.

### 4. Better analytics

Add charts and more detailed reporting for:

- Monthly trends
- Category spending
- Department spending
- Duplicate claims
- Approval/rejection rates

### 5. Notifications

Add email or in-app notifications when:

- A claim is submitted
- A claim is approved/rejected
- A claim is paid
- A duplicate is detected

### 6. Automated testing

Add unit and integration tests for:

- Authentication
- Permissions
- Claim validation
- Duplicate detection
- Status transitions
- Approval and payment workflows

### 7. Production hardening

Improve:

- Error handling
- Logging
- Monitoring
- Rate limiting
- Secure file access
- Configuration management

---

## AI Tools Used

### Google Gemini

Used for:

- Extracting structured expense information from pasted receipt text
- Reducing manual data entry

### ChatGPT

Used during development for:

- Development assistance
- Debugging
- Architecture and implementation guidance
- Testing ideas
- Documentation assistance

AI-generated suggestions were reviewed and integrated into the application based on the requirements of the task.

---

## Testing

The application was tested across the three roles.

### Employee

- Login
- Session persistence
- Claim creation
- Manual entry
- AI extraction
- Receipt upload
- Claim history
- Duplicate detection

### Manager

- Login
- Team claim visibility
- Claim review
- Approval
- Rejection
- Own-claim submission
- Self-approval restriction

### Finance

- Login
- Approved claim visibility
- Marking claims as paid
- Monthly analytics
- Spending by person
- Spending by category
- Monthly limit tracking

The deployed application was also tested using the public Render URL.

---

## Demo Flow

For a quick demonstration:

1. Login as Employee
2. Create a claim using receipt text
3. Extract the receipt information using AI
4. Review and correct the extracted information
5. Submit the claim
6. Login as Manager
7. Review and approve the employee claim
8. Login as Finance
9. Mark the approved claim as paid
10. Open analytics and review monthly spending

---

## Repository

GitHub:

https://github.com/vkrvkr763-lgtm/expense-claims

Live Application:

https://expense-claims-8heb.onrender.com
