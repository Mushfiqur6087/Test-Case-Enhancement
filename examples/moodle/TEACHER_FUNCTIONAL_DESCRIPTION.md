# Moodle Teacher Functional Description

**Test Account:** testteacher / Test@1234


## 1. Login

The login page displays a centered card with the heading "Log in to Moodle Test Site" at the top. The form contains a Username field and a Password field, followed by a blue "Log in" button. Below the button is a "Lost password?" link which is currently disabled on this test site. A separate section below states "Some courses may allow guest access" with an "Access as a guest" button that allows users to browse courses without authentication. A "Cookies notice" button at the bottom provides information about cookie usage. When the teacher enters valid credentials and clicks Log in, the system validates against the database and redirects to the Dashboard upon success. If the credentials are invalid or fields are empty, an error message appears and the username field remains populated for correction.

## 2. Dashboard

The Dashboard serves as the teacher's home base after logging in. At the top, a personalized greeting displays "Hi, [Name]!" with a waving hand emoji. The main content area displays the Timeline block and Calendar block. The Timeline block shows upcoming activities and deadlines across all courses, with a "Next 7 days" dropdown to filter the time range, a "Sort by dates" dropdown for ordering, and a search field to find activities by type or name. When no activities are pending, it displays "No activities require action" with an icon. The Calendar block shows a monthly view with the current month and year displayed prominently. It includes an "All courses" dropdown to filter events by course, a "New event" button to create calendar entries, and navigation arrows to move between months (showing previous and next month names). The current date is highlighted, and dates with events display event names. At the bottom of the Calendar block, "Full calendar" and "Import or export calendars" links provide access to additional calendar features.

When Edit mode is toggled on, the Dashboard displays additional controls. A "Reset page to default" button appears at the top right to restore the default layout. A "+ Add a block" button appears below the Dashboard heading, allowing teachers to add new blocks. Clicking this opens an "Add a block" modal with available block types including: Comments, Course overview, Latest badges, Learning plans, Logged in user, Mentees, Online users, Private files, Random glossary entry, Recently accessed courses, Starred courses, Tags, Text, and Upcoming events. The modal has an X button to close and a "Cancel" button. Each existing block displays a move icon (four arrows) and a three-dot menu for block options when in edit mode.

## 3. My Courses

The My Courses page provides a view of all courses where the teacher is enrolled. The page has a "My courses" heading with "Course overview" as a subheading. The page displays courses as visual cards showing the course image, course name as a clickable link, and the category name below. An "All" dropdown allows filtering courses by status. A "Search" field allows teachers to find specific courses by typing part of the course name. A "Sort by course name" dropdown allows sorting the course list. A "Card" dropdown allows switching between different view layouts. Each course card includes a three-dot menu at the bottom right which opens a dropdown with "Star this course" and "Remove from view" options. Clicking a course name navigates directly to that course's main page.

## 4. Course Page

The Course Page displays the complete course content organized into sections. At the top, the course full name appears as a heading, followed by a horizontal navigation bar with tabs for Course, Settings, Participants, Grades, Activities, and a More dropdown. The main content area shows the course sections, each with a collapsible chevron arrow and section name. A "Collapse all" link at the top right allows collapsing all sections at once. Each section contains activities and resources such as assignments, forums, files, and pages, each with an icon indicating its type and the activity name as a clickable link. The Course Index on the left side provides a collapsible navigation tree showing all sections and activities. At the top of the Course Index, a "Close course index" button allows hiding the sidebar. Sections in the Course Index can be expanded or collapsed to show their contained activities.

## 5. Adding Activities

To add activities or resources to a course, the teacher must first enable editing by toggling "Edit mode" on using the toggle in the top-right corner. When enabled, the course page transforms to reveal content management controls. A "Bulk actions" link with a pencil icon appears near the course title for managing multiple items. Each section displays a pencil icon next to the section name for inline editing, and a three-dot menu on the right for additional section options. Each activity shows a pencil icon for inline editing and a three-dot menu for activity options.

A "+" button appears at the bottom of each section. Clicking this button shows a dropdown with two options: "Activity or resource" and "Subsection". Selecting "Activity or resource" opens the Activity Chooser modal. The Activity Chooser has a title "Add an activity or resource" with an X button to close. A Search field at the top allows filtering by name. The left sidebar shows category filters: All, Assessment, Collaboration, Communication, Resources, and Interactive content. The main area displays a grid of available activities and resources, each with an icon, name, an info button, and a star button to mark as favorite. Available options include Assignment, Book, Choice, Database, Feedback, File, Folder, Forum, Glossary, H5P, IMS content package, Lesson, Page, Quiz, SCORM package, Text and media area, URL, Wiki, and Workshop. An "Add" button at the bottom right confirms the selection.

When adding an Assignment, the configuration form appears with the heading "New Assignment" and an "Expand all" link to expand all sections. The form contains multiple collapsible sections:

The General section contains an "Assignment name" field (required), a "Description" rich text editor with formatting toolbar, a "Display description on course page" checkbox, an "Activity instructions" rich text editor, and an "Additional files" upload area with drag-and-drop support showing "Maximum size for new files: 100 MB".

The Availability section contains date/time settings with Enable checkboxes for "Allow submissions from", "Due date", "Cut-off date", and "Remind me to grade by". Each has day, month, year, hour, and minute dropdowns plus a calendar picker icon. An "Always show description" checkbox is also present.

The Submission types section contains checkboxes for "Online text" and "File submissions", a "Maximum number of uploaded files" dropdown, a "Maximum submission size" dropdown showing "Site upload limit (100 MB)", and an "Accepted file types" field with a "Choose" button.

Additional collapsible sections include: Feedback types, Submission settings, Group submission settings, Notifications, Grade, Common module settings, Restrict access, Completion conditions, Tags, and Competencies. A "Send content change notification" checkbox appears near the bottom. Required fields are indicated with a "Required" label.

At the bottom of the form, three buttons appear: "Save and return to course" creates the activity and returns to the course page, "Save and display" creates and opens the activity, and "Cancel" discards changes.

## 6. Course Settings

The Course Settings page allows teachers to configure course properties and is accessed from the Settings tab in the course navigation without requiring Edit mode. A "Collapse all" link at the top right allows collapsing all sections. The form contains multiple collapsible sections:

General section contains Course full name (required), Course short name (required), Course category field with search dropdown (required), Course visibility dropdown, Course start date with date/time dropdowns, Course end date with Enable checkbox and date/time dropdowns, and Course ID number field.

Description section contains Course summary rich text editor and a file upload area for course images.

Course format section contains Format dropdown, Hidden sections dropdown, and Course layout dropdown.

Appearance section contains Force language dropdown, Number of announcements dropdown, Show gradebook to students dropdown, Show activity reports dropdown, and Show activity dates dropdown.

Files and uploads section contains Maximum upload size dropdown.

Completion tracking section contains Enable completion tracking dropdown and Show activity completion conditions dropdown.

Groups section contains Group mode dropdown, Force group mode dropdown, and Default grouping dropdown.

Tags section contains Tags field with search dropdown.

Required fields are indicated with a "Required" label. The form has "Save and display" and "Cancel" buttons at the bottom.

## 7. Participants

The Participants page displays all users enrolled in the course. At the top, an "Enrolled users" dropdown and an "Enrol users" button allow managing course enrollment. Below this, a Match filter system provides flexible filtering with "Any" and "Select" dropdowns, an X button to remove filters, and an "+ Add condition" link to add more filter criteria. "Clear filters" and "Apply filters" buttons control the filter application. A count displays the number of participants found (e.g., "4 participants found").

Alphabetical filter buttons appear for First name and Last name, showing "All" and individual letters A through Z to quickly filter participants by name initials.

The main content area shows a table with the following columns: a checkbox for bulk selection, First name / Last name (sortable with arrows), Email address, Roles (with a pencil icon for editing roles), Groups, Last access to course, and Status. Each participant row displays a circular icon with user initials, the participant's name as a clickable link, their email address, their role, group membership, last access time, and an Active status badge. Action icons appear at the end of each row: an info icon to view details, an edit icon, and a delete icon.

At the bottom of the table, "With selected users..." text appears with a "Choose..." dropdown for bulk actions on selected participants. An "Enrol users" button at the bottom right opens a dialog to search for and enroll additional users, assigning them a role and optionally setting enrollment duration. Teachers can click any participant name to view their profile or access their grade report.

## 8. Assignment (Teacher View)

The Assignment page displays breadcrumbs showing the navigation path and an assignment icon with the heading "ASSIGNMENT" and the assignment name. Tabs at the top provide access to Assignment, Settings, Submissions, Advanced grading, and More dropdown. The page shows the Opened date, Due date, and assignment description text. A "Grade" button allows teachers to start grading. The Grading summary section displays a table with rows for Hidden from students (Yes/No), Participants count, Submitted count, Needs grading count, and Time remaining until due date.

## 9. Assignment Submissions

The Submissions tab displays all student submissions in a table format. At the top, a "Search users" field, "Filter by name" dropdown, Status filter (defaulting to "All"), and Advanced dropdown allow filtering submissions. A "Grade" button appears on the right, and a "Quick grading" checkbox with "Actions" dropdown provide grading options. The table columns include: Select (checkbox), First name / Last name (sortable), Email address, Status, Grade, Last modified (submission), Online text, File submissions, Submission comments, Last modified (grade), Feedback comments, Feedback files, and Final grade. Each row shows a student with circular icon containing initials, their name as a link, email address, and submission status (e.g., "No submission"). Three-dot menus in various columns provide additional options for each submission.

## 10. Advanced Grading

The Advanced grading tab provides options for creating advanced grading methods. At the top, "Change active grading method to" dropdown is set to "Rubric". Two card options are displayed: "Define new grading form from scratch" and "Create new grading form from a template". A notification message states: "Please note: the advanced grading form is not ready at the moment. Simple grading method will be used until the form has a valid status." This indicates that advanced grading features like rubrics need to be set up before they can be used for grading assignments.

## 11. Gradebook (Grader Report)

The Gradebook page is accessed via the Grades tab in the course navigation. At the top, a "Grader report" dropdown allows selecting different report types, a "Search users" field filters the grade table, and a "Filter by name" dropdown provides additional filtering. The main content displays a spreadsheet-style table with the course name header showing a three-dot menu. The first column shows "First name / Last name" with user icons and names as links, followed by an "Email address" column. Subsequent columns represent individual assignments (e.g., "BUS301 - Case Study Analysis", "BUS301 - Business Plan Draft", "BUS301 - Final Presentation") and an "r" column, with a "Course total" column at the end. Each column header has a three-dot menu. Grade cells contain either numeric values or are empty, with three-dot menus for additional options. An "Overall average" row at the bottom shows averages for each column. A "Save changes" button appears at the bottom of the page when Edit mode is enabled.

## 12. Profile

The Profile page displays the user's information and is accessed by clicking the user initials in the top navigation bar and selecting Profile. At the top, the user's circular icon with initials is shown alongside their full name and a "Message" button. Below the name, a description text displays the user's profile description. When Edit mode is enabled, a "Reset page to default" button appears at the top right.

The page displays several information cards. The User details card shows an "Edit profile" link in the top right corner, the Email address with visibility note (e.g., "Visible to other course participants"), and the Timezone setting. The Privacy and policies card contains a "Data retention summary" link. The Course details card lists all Course profiles with links to each enrolled course. The Miscellaneous card provides links to Blog entries, Forum posts, Forum discussions, and Learning plans. The Reports card contains links to Browser sessions and Grades overview. The Login activity card displays First access to site and Last access to site with dates and relative time indicators.

Clicking "Edit profile" opens the profile editing form with the user's name as a heading and an "Expand all" link. The form contains collapsible sections:

General section contains First name (required), Last name (required), Email address (required), Email visibility dropdown (e.g., "Visible to course participants"), MoodleNet profile ID field, City/town field, Select a country dropdown, Timezone dropdown, and Description rich text editor.

User picture section shows Current picture (or "None" if not set), New picture upload area with drag-and-drop support showing "Maximum file size: 100 MB, maximum number of files: 1", accepted file types for images (.gif, .jpe, .jpeg, .jpg, .png, .webp), and Picture description field.

Additional collapsible sections include Additional names, Interests, and Optional. Required fields are marked with "Required" label. The form has "Update profile" and "Cancel" buttons at the bottom.

## Navigation

The Moodle navigation structure provides multiple ways to access features throughout the system.

The Top Navigation Bar appears on every page and contains the site name "MoodleTest" on the left which links to the home page. Next to it are links for Home, Dashboard, and My courses that provide quick access to the main areas of the system. On the right side of the navigation bar, a notifications bell icon shows alerts when clicked, a messaging icon opens the messaging drawer for conversations, and the user's initials displayed in a circular icon (e.g., "JT") opens the user menu when clicked.

Clicking on the user initials icon opens the User Menu dropdown. The menu displays Profile at the top which navigates to the user's profile page. Below that, Grades shows the user's personal grades across all courses. Calendar opens the calendar view. Private files provides access to personal file storage. Reports shows user activity reports. A separator line divides these items from Preferences, which opens user settings. Another separator appears before the final Log out option that ends the session and returns to the login page.

When viewing a course, Course Navigation tabs appear as a horizontal bar below the course title. The tabs include Course (the main content view), Settings (course configuration), Participants (enrolled users), Grades (gradebook), Activities (list of all activities), and a More dropdown for additional options. 

When viewing an assignment or other activity, Assignment Navigation displays breadcrumbs at the top showing the navigation path from the course (e.g., "BUS301 / New section / BUS301 - Case Study Analysis"). Each breadcrumb segment is a clickable link to navigate back to that level. Below the breadcrumbs, an assignment icon and "ASSIGNMENT" label appear above the assignment name. Activity-specific tabs appear below the title: Assignment (the main view), Settings (activity configuration), Submissions (student submission list), Advanced grading (rubrics and grading forms), and a More dropdown for additional options. These tabs change based on the activity type being viewed.
