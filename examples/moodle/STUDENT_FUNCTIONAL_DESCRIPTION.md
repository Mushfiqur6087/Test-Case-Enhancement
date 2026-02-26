# Moodle Student Functional Description

**Test Account:** teststudent / Test@1234


## 1. Login

The login page displays a centered card with the heading "Log in to Moodle Test Site" at the top. The form contains a Username field and a Password field, followed by a blue "Log in" button. Below the button is a "Lost password?" link which is currently disabled on this test site. A separate section below states "Some courses may allow guest access" with an "Access as a guest" button that allows users to browse courses without authentication. A "Cookies notice" button at the bottom provides information about cookie usage. When the student enters valid credentials and clicks Log in, the system validates against the database and redirects to the Dashboard upon success. If the credentials are invalid or fields are empty, an error message appears and the username field remains populated for correction.

## 2. Dashboard

The Dashboard serves as the student's home base after logging in. At the top, a personalized greeting displays "Hi, [Name]!" with a waving hand emoji. The main content area displays the Timeline block and Calendar block. The Timeline block shows upcoming activities and deadlines across all enrolled courses, with a "Next 7 days" dropdown to filter the time range, a "Sort by dates" dropdown for ordering, and a search field to find activities by type or name. When no activities are pending, it displays "No activities require action" with an icon. The Calendar block shows a monthly view with the current month and year displayed prominently. It includes an "All courses" dropdown to filter events by course, a "New event" button to create personal calendar entries, and navigation arrows to move between months (showing previous and next month names). The current date is highlighted, and dates with events display event names. At the bottom of the Calendar block, "Full calendar" and "Import or export calendars" links provide access to additional calendar features.

When Edit mode is toggled on, the Dashboard displays additional controls. A "Reset page to default" button appears at the top right to restore the default layout. A "+ Add a block" button appears below the Dashboard heading, allowing students to add new blocks to personalize their dashboard. Clicking this opens an "Add a block" page with the heading "Moodle Test Site" and "Add a block" subheading. The page lists available block types in a vertical list: Comments, Course overview, Latest announcements, Latest badges, Learning plans, Logged in user, Mentees, Online users, Private files, Random glossary entry, Recently accessed courses, Starred courses, Tags, Text, and Upcoming events. A "Cancel" link at the bottom returns to the Dashboard without adding a block. Each existing block displays a move icon (four arrows) and a three-dot menu for block options when in edit mode. Students can rearrange, configure, or remove blocks to customize their dashboard layout.

## 3. My Courses

The My Courses page provides a view of all courses where the student is enrolled. The page has a "My courses" heading with "Course overview" as a subheading. The page displays courses as visual cards showing the course image, course name as a clickable link, and the category name below. An "All" dropdown allows filtering courses by status. A "Search" field allows students to find specific courses by typing part of the course name. A "Sort by course name" dropdown allows sorting the course list. A "Card" dropdown allows switching between different view layouts. Each course card includes a three-dot menu at the bottom right which opens a dropdown with "Star this course" and "Remove from view" options. Clicking a course name navigates directly to that course's main page.

## 4. Course Page (View Only)

The Course Page displays the complete course content organized into sections. At the top, the course full name appears as a heading (e.g., "Business Management Fundamentals"), followed by a horizontal navigation bar with tabs for Course, Participants, Grades, Activities, and Competencies. Unlike teachers, students do not see the Settings tab and cannot enable Edit mode on course pages.

The main content area shows the course sections, each with a collapsible chevron arrow and section name (e.g., "General", "New section", "New subsection"). A "Collapse all" link at the top right allows collapsing all sections at once. Each section contains activities and resources such as assignments, forums, files, and pages, each with an icon indicating its type and the activity name as a clickable link. Activities include items like "Announcements" (forum icon), "BUS301 Course Overview" (page icon), "BUS301 Business Discussion" (forum icon), "BUS301 - Case Study Analysis" (assignment icon), "BUS301 - Business Plan Draft" (assignment icon), and "BUS301 - Final Presentation" (assignment icon).

The Course Index on the left side provides a collapsible navigation tree showing all sections and activities. At the top of the Course Index, a close button (X) allows hiding the sidebar. Sections in the Course Index can be expanded or collapsed to show their contained activities. Clicking any activity in the Course Index navigates directly to that activity.

## 5. Participants

The Participants page displays all users enrolled in the course and is accessed via the Participants tab in the course navigation. At the top, a Match filter system provides flexible filtering with "Any" and "Select" dropdowns, an X button to remove filters, and an "+ Add condition" link to add more filter criteria. "Clear filters" and "Apply filters" buttons control the filter application. A count displays the number of participants found.

Alphabetical filter buttons appear for First name and Last name, showing "All" and individual letters A through Z to quickly filter participants by name initials.

The main content area shows a table with columns for checkbox selection, First name / Last name (sortable), Roles, Groups, and Last access to course. Each participant row displays a circular icon with user initials, the participant's name as a clickable link, their role (Teacher or Student), group membership, and last access time.

At the bottom of the table, "With selected users..." text appears with a "Choose..." dropdown for actions on selected participants. Students can click any participant name to view their profile. Unlike teachers, students cannot enrol or unenrol users, edit roles, or access enrollment management features.

## 6. Grades (User Report)

The Grades page displays the student's own grades for the course and is accessed via the Grades tab in the course navigation. At the top, a "User report" dropdown indicates the current report view. The page displays the student's name with their initials icon.

The main content area shows a grade table with columns for Grade item (listing the course name as a collapsible header and all graded activities below it), Calculated weight (showing the weight percentage for each item), Grade (displaying the earned grade or "-" if not yet graded, with a three-dot menu), Range (showing the grade range), Percentage (showing the percentage achieved), Feedback (displaying any feedback from the teacher), and Contribution to course total (showing how much each grade contributes to the final grade).

Each graded activity is listed with its type label (e.g., "ASSIGNMENT") above the activity name as a clickable link. Items that have not been submitted or graded show "(Empty)" in the Calculated weight column. At the bottom, an "AGGREGATION Course total" row displays the overall course grade.

Students can only view their own grades and cannot see other students' grades or access the full gradebook that teachers use.

## 7. Assignment (Student View)

The Assignment page displays the assignment details and submission interface. At the top, breadcrumbs show the navigation path from the course to the assignment. An assignment icon appears next to the assignment name heading.

The page displays the Opened date and time when the assignment became available, the Due date for submission deadline, and the Description containing the assignment instructions.

A blue "Add submission" button allows students to submit their work. Clicking this button opens the submission form where students can enter online text, upload files, or both depending on the assignment configuration.

The Submission status section displays a table showing the Submission status (current state such as "No submissions have been made yet" or "Submitted for grading"), Grading status (whether the submission has been graded), Time remaining (countdown until the due date), Last modified (when the submission was last updated), and Submission comments (a collapsible section for adding comments).

After submitting, students can view their submission, edit it (if allowed before the due date), or remove it. Once graded, the grade and feedback from the teacher will appear on this page.

## 8. Activities

The Activities page provides an overview of all activities in the course, organized by type. It is accessed via the Activities tab in the course navigation. At the top, the page heading displays "Activities" with a description: "An overview of all activities in the course, with dates and other information."

Activities are grouped by type in collapsible sections. The Assignments section displays a table with columns for Name (the assignment name as a clickable link with its section name below), Due date (the deadline), and Submission status (the student's submission state such as "Submitted for grading" or "No submission").

The Forums section (collapsible with > arrow) lists all forum activities in the course. The Resources section (collapsible with > arrow) lists all resources like files and pages in the course.

Each section can be expanded or collapsed by clicking the arrow icon. Clicking any activity name navigates directly to that activity's page.

## 9. Profile

The Profile page displays the student's information and is accessed by clicking the user initials in the top navigation bar and selecting Profile. At the top, the user's circular icon with initials is shown alongside their full name and a "Message" button. Below the name, a description text displays the user's profile description. When Edit mode is enabled, a "Reset page to default" button appears at the top right.

The page displays several information cards. The User details card shows an "Edit profile" link in the top right corner, the Email address with visibility note (e.g., "Visible to other course participants"), and the Timezone setting. The Privacy and policies card contains a "Data retention summary" link. The Course details card lists all Course profiles with links to each enrolled course. The Miscellaneous card provides links to Blog entries, Forum posts, Forum discussions, and Learning plans. The Reports card contains links to Browser sessions and Grades overview. The Login activity card displays First access to site and Last access to site with dates and relative time indicators.

Clicking "Edit profile" opens the profile editing form with the user's name as a heading and an "Expand all" link. The form contains collapsible sections including the General section (with First name, Last name, Email address, Email visibility dropdown, MoodleNet profile ID field, City/town field, Select a country dropdown, Timezone dropdown, and Description rich text editor), the User picture section (showing Current picture, New picture upload area with drag-and-drop support, and Picture description field), and additional sections for Additional names, Interests, and Optional fields. Required fields are marked with "Required" label. The form has "Update profile" and "Cancel" buttons at the bottom.

Note: Students have the same profile editing capabilities as teachers, but they can only modify their own profile and student-related settings.

## Navigation

The Moodle navigation structure provides multiple ways to access features throughout the system.

The Top Navigation Bar appears on every page and contains the site name "MoodleTest" on the left which links to the home page. Next to it are links for Home, Dashboard, and My courses that provide quick access to the main areas of the system. On the right side of the navigation bar, a notifications bell icon shows alerts when clicked, a messaging icon opens the messaging drawer for conversations, and the user's initials displayed in a circular icon opens the user menu when clicked.

Clicking on the user initials icon opens the User Menu dropdown. The menu displays Profile at the top which navigates to the user's profile page. Below that, Grades shows the user's personal grades across all courses. Calendar opens the calendar view. Private files provides access to personal file storage. Reports shows user activity reports. A separator line divides these items from Preferences, which opens user settings. Another separator appears before the final Log out option that ends the session and returns to the login page.

When viewing a course, Course Navigation tabs appear as a horizontal bar below the course title. For students, the tabs include Course (the main content view), Participants (enrolled users), Grades (personal grades), Activities (list of all activities), and Competencies. Note that students do not see the Settings tab that teachers have access to.

When viewing an assignment or other activity, Activity Navigation displays breadcrumbs at the top showing the navigation path from the course. Each breadcrumb segment is a clickable link to navigate back to that level. Below the breadcrumbs, an activity icon and the activity name appear as the page heading.

The Course Index sidebar on the left side of course pages provides quick navigation to all sections and activities. It shows a hierarchical tree structure with section names, activities within each section, expand/collapse arrows for sections with multiple items, and a close button (X) at the top to hide the sidebar. Clicking any item in the Course Index navigates directly to that section or activity. The currently selected activity is highlighted in the Course Index.