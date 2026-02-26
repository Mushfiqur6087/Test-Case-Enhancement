<?php
/**
 * Moodle Test Environment Setup Script
 * Creates consistent test data for functional testing
 * 
 * This script creates:
 * - 5 test users (admin, 2 teachers, 2 students)
 * - 5 test courses with activities
 * - Enrollments for all users
 * - Assignments that students can submit
 * - A credentials.txt file documenting everything
 */

define('CLI_SCRIPT', true);

require(__DIR__ . '/config.php');
require_once($CFG->libdir . '/clilib.php');
require_once($CFG->libdir . '/adminlib.php');
require_once($CFG->dirroot . '/user/lib.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->libdir . '/enrollib.php');
require_once($CFG->libdir . '/gradelib.php');
require_once($CFG->dirroot . '/mod/assign/lib.php');

// Ensure we're running as admin
\core\session\manager::set_user(get_admin());

echo "==============================================\n";
echo "MOODLE TEST ENVIRONMENT SETUP\n";
echo "==============================================\n\n";

// ============================================
// 1. CREATE TEST USERS
// ============================================
echo "Creating test users...\n";

$test_users = [
    [
        'username' => 'testadmin',
        'password' => 'Test@1234',
        'firstname' => 'Alice',
        'lastname' => 'Administrator',
        'email' => 'testadmin@test.local',
        'role' => 'manager',
        'description' => 'Test Manager Account'
    ],
    [
        'username' => 'testteacher',
        'password' => 'Test@1234',
        'firstname' => 'John',
        'lastname' => 'Teacher',
        'email' => 'teacher@test.local',
        'role' => 'editingteacher',
        'description' => 'Test Teacher Account'
    ],
    [
        'username' => 'testteacher2',
        'password' => 'Test@1234',
        'firstname' => 'Mary',
        'lastname' => 'Instructor',
        'email' => 'teacher2@test.local',
        'role' => 'editingteacher',
        'description' => 'Test Teacher Account 2'
    ],
    [
        'username' => 'teststudent',
        'password' => 'Test@1234',
        'firstname' => 'Jane',
        'lastname' => 'Student',
        'email' => 'student@test.local',
        'role' => 'student',
        'description' => 'Test Student Account'
    ],
    [
        'username' => 'teststudent2',
        'password' => 'Test@1234',
        'firstname' => 'Bob',
        'lastname' => 'Learner',
        'email' => 'student2@test.local',
        'role' => 'student',
        'description' => 'Test Student Account 2'
    ]
];

$created_users = [];

foreach ($test_users as $userdata) {
    // Check if user already exists
    if ($existing = $DB->get_record('user', ['username' => $userdata['username']])) {
        echo "  - User '{$userdata['username']}' already exists (ID: {$existing->id})\n";
        $created_users[$userdata['username']] = $existing;
        $created_users[$userdata['username']]->plainpassword = $userdata['password'];
        $created_users[$userdata['username']]->rolename = $userdata['role'];
        continue;
    }
    
    $user = new stdClass();
    $user->username = $userdata['username'];
    $user->password = hash_internal_user_password($userdata['password']);
    $user->firstname = $userdata['firstname'];
    $user->lastname = $userdata['lastname'];
    $user->email = $userdata['email'];
    $user->confirmed = 1;
    $user->mnethostid = $CFG->mnet_localhost_id;
    $user->timecreated = time();
    $user->timemodified = time();
    $user->description = $userdata['description'];
    
    $user->id = $DB->insert_record('user', $user);
    $user->plainpassword = $userdata['password'];
    $user->rolename = $userdata['role'];
    $created_users[$userdata['username']] = $user;
    
    echo "  + Created user '{$userdata['username']}' (ID: {$user->id})\n";
}

// ============================================
// 2. CREATE TEST COURSE CATEGORY
// ============================================
echo "\nCreating test category...\n";

$category_name = 'Test Courses';
if (!$category = $DB->get_record('course_categories', ['name' => $category_name, 'depth' => 1])) {
    $category = core_course_category::create([
        'name' => $category_name,
        'description' => 'Courses for functional testing - DO NOT DELETE',
        'idnumber' => 'TEST_CAT'
    ]);
    echo "  + Created category '{$category_name}'\n";
} else {
    $category = core_course_category::get($category->id);
    echo "  - Category '{$category_name}' already exists\n";
}

// ============================================
// 3. DEFINE 5 TEST COURSES
// ============================================
$courses_config = [
    [
        'shortname' => 'CS101',
        'fullname' => 'Introduction to Computer Science',
        'summary' => '<p>Learn the fundamentals of computer science including programming basics, algorithms, and data structures.</p>',
        'teachers' => ['testteacher'],
        'students' => ['teststudent', 'teststudent2'],
        'assignments' => [
            ['name' => 'CS101 - Assignment 1: Hello World Program', 'intro' => '<p>Write your first program that outputs "Hello World".</p><p><strong>Submit:</strong> Source code file (.py, .java, or .c)</p>', 'grade' => 100],
            ['name' => 'CS101 - Assignment 2: Variables and Data Types', 'intro' => '<p>Create a program demonstrating different variable types.</p>', 'grade' => 100],
        ],
        'forum' => 'CS101 Discussion Forum',
        'page' => ['name' => 'CS101 Course Introduction', 'content' => '<h3>Welcome to CS101!</h3><p>This course covers fundamental computer science concepts.</p><h4>Topics:</h4><ul><li>Programming Basics</li><li>Variables and Data Types</li><li>Control Structures</li><li>Functions</li></ul>']
    ],
    [
        'shortname' => 'MATH201',
        'fullname' => 'Calculus I',
        'summary' => '<p>Introduction to differential and integral calculus. Topics include limits, derivatives, and basic integration.</p>',
        'teachers' => ['testteacher', 'testteacher2'],
        'students' => ['teststudent'],
        'assignments' => [
            ['name' => 'MATH201 - Problem Set 1: Limits', 'intro' => '<p>Solve the following limit problems. Show all your work.</p>', 'grade' => 50],
            ['name' => 'MATH201 - Problem Set 2: Derivatives', 'intro' => '<p>Calculate derivatives for the given functions.</p>', 'grade' => 50],
            ['name' => 'MATH201 - Midterm Project', 'intro' => '<p>Complete the midterm project covering limits and derivatives.</p>', 'grade' => 100],
        ],
        'forum' => 'MATH201 Q&A Forum',
        'page' => ['name' => 'MATH201 Syllabus', 'content' => '<h3>Calculus I Syllabus</h3><p>Week 1-3: Limits</p><p>Week 4-6: Derivatives</p><p>Week 7-9: Applications</p><p>Week 10-12: Integration Intro</p>']
    ],
    [
        'shortname' => 'ENG102',
        'fullname' => 'English Composition',
        'summary' => '<p>Develop your writing skills through essays, research papers, and creative writing exercises.</p>',
        'teachers' => ['testteacher2'],
        'students' => ['teststudent', 'teststudent2'],
        'assignments' => [
            ['name' => 'ENG102 - Essay 1: Personal Narrative', 'intro' => '<p>Write a 500-word personal narrative essay.</p><p><strong>Format:</strong> PDF or Word document</p>', 'grade' => 100],
            ['name' => 'ENG102 - Essay 2: Argumentative Essay', 'intro' => '<p>Write a 750-word argumentative essay on a topic of your choice.</p>', 'grade' => 100],
        ],
        'forum' => 'ENG102 Writing Workshop',
        'page' => ['name' => 'ENG102 Writing Guidelines', 'content' => '<h3>Writing Guidelines</h3><p>All submissions must be:</p><ul><li>Double-spaced</li><li>12pt Times New Roman font</li><li>1-inch margins</li><li>MLA format citations</li></ul>']
    ],
    [
        'shortname' => 'PHY101',
        'fullname' => 'Physics for Beginners',
        'summary' => '<p>Introduction to physics concepts including mechanics, thermodynamics, and basic electricity.</p>',
        'teachers' => ['testteacher'],
        'students' => ['teststudent2'],
        'assignments' => [
            ['name' => 'PHY101 - Lab Report 1: Motion', 'intro' => '<p>Complete the motion experiment and submit your lab report.</p>', 'grade' => 100],
            ['name' => 'PHY101 - Lab Report 2: Forces', 'intro' => '<p>Analyze forces in the given scenarios and submit your findings.</p>', 'grade' => 100],
        ],
        'forum' => 'PHY101 Lab Discussion',
        'page' => ['name' => 'PHY101 Lab Safety Rules', 'content' => '<h3>Laboratory Safety</h3><p>Always follow safety protocols:</p><ol><li>Wear safety goggles</li><li>No food or drinks in lab</li><li>Report accidents immediately</li></ol>']
    ],
    [
        'shortname' => 'BUS301',
        'fullname' => 'Business Management Fundamentals',
        'summary' => '<p>Learn core business management principles including planning, organizing, leading, and controlling.</p>',
        'teachers' => ['testteacher', 'testteacher2'],
        'students' => ['teststudent', 'teststudent2'],
        'assignments' => [
            ['name' => 'BUS301 - Case Study Analysis', 'intro' => '<p>Analyze the provided business case study and submit your analysis report.</p>', 'grade' => 100],
            ['name' => 'BUS301 - Business Plan Draft', 'intro' => '<p>Create a draft business plan for a startup of your choice.</p>', 'grade' => 150],
            ['name' => 'BUS301 - Final Presentation', 'intro' => '<p>Prepare and submit your final presentation slides.</p>', 'grade' => 100],
        ],
        'forum' => 'BUS301 Business Discussion',
        'page' => ['name' => 'BUS301 Course Overview', 'content' => '<h3>Business Management Fundamentals</h3><p>This course prepares you for real-world business challenges.</p><h4>Learning Objectives:</h4><ul><li>Understand management functions</li><li>Develop leadership skills</li><li>Create business plans</li><li>Analyze business cases</li></ul>']
    ]
];

// ============================================
// 4. CREATE COURSES AND CONTENT
// ============================================
echo "\nCreating courses and content...\n";

$created_courses = [];
$enrollment_data = [];

// Get role IDs
$roles = $DB->get_records('role', [], '', 'shortname, id');
$enrol_plugin = enrol_get_plugin('manual');

foreach ($courses_config as $course_config) {
    echo "\n  Course: {$course_config['fullname']}\n";
    
    // Check if course exists
    if (!$course = $DB->get_record('course', ['shortname' => $course_config['shortname']])) {
        $coursedata = new stdClass();
        $coursedata->fullname = $course_config['fullname'];
        $coursedata->shortname = $course_config['shortname'];
        $coursedata->category = $category->id;
        $coursedata->summary = $course_config['summary'];
        $coursedata->summaryformat = FORMAT_HTML;
        $coursedata->format = 'topics';
        $coursedata->numsections = 5;
        $coursedata->visible = 1;
        $coursedata->startdate = time();
        $coursedata->enddate = time() + (180 * 24 * 60 * 60); // 6 months
        $coursedata->enablecompletion = 1;
        
        $course = create_course($coursedata);
        echo "    + Created course (ID: {$course->id})\n";
    } else {
        echo "    - Course already exists (ID: {$course->id})\n";
    }
    
    $created_courses[$course_config['shortname']] = $course;
    
    // Get or create manual enrolment instance
    $enrol_instances = enrol_get_instances($course->id, true);
    $manual_instance = null;
    foreach ($enrol_instances as $instance) {
        if ($instance->enrol === 'manual') {
            $manual_instance = $instance;
            break;
        }
    }
    if (!$manual_instance) {
        $enrolid = $enrol_plugin->add_instance($course);
        $manual_instance = $DB->get_record('enrol', ['id' => $enrolid]);
    }
    
    $course_context = context_course::instance($course->id);
    
    // Enroll teachers
    foreach ($course_config['teachers'] as $teacher_username) {
        $teacher = $created_users[$teacher_username];
        if (!is_enrolled($course_context, $teacher->id)) {
            $enrol_plugin->enrol_user($manual_instance, $teacher->id, $roles['editingteacher']->id);
            echo "    + Enrolled '{$teacher_username}' as Teacher\n";
        }
        $enrollment_data[$teacher_username]['courses'][] = [
            'shortname' => $course_config['shortname'],
            'fullname' => $course_config['fullname'],
            'role' => 'Teacher'
        ];
    }
    
    // Enroll students
    foreach ($course_config['students'] as $student_username) {
        $student = $created_users[$student_username];
        if (!is_enrolled($course_context, $student->id)) {
            $enrol_plugin->enrol_user($manual_instance, $student->id, $roles['student']->id);
            echo "    + Enrolled '{$student_username}' as Student\n";
        }
        $enrollment_data[$student_username]['courses'][] = [
            'shortname' => $course_config['shortname'],
            'fullname' => $course_config['fullname'],
            'role' => 'Student'
        ];
    }
    
    // Create page content
    if (!empty($course_config['page'])) {
        $page_exists = $DB->record_exists_sql(
            "SELECT 1 FROM {page} p JOIN {course_modules} cm ON p.id = cm.instance 
             JOIN {modules} m ON m.id = cm.module 
             WHERE cm.course = ? AND p.name = ? AND m.name = 'page'",
            [$course->id, $course_config['page']['name']]
        );
        
        if (!$page_exists) {
            $module = $DB->get_record('modules', ['name' => 'page']);
            
            $page = new stdClass();
            $page->course = $course->id;
            $page->name = $course_config['page']['name'];
            $page->intro = '<p>Course information page</p>';
            $page->introformat = FORMAT_HTML;
            $page->content = $course_config['page']['content'];
            $page->contentformat = FORMAT_HTML;
            $page->display = 5;
            $page->timemodified = time();
            $page->id = $DB->insert_record('page', $page);
            
            $cm = new stdClass();
            $cm->course = $course->id;
            $cm->module = $module->id;
            $cm->instance = $page->id;
            $cm->section = 1;
            $cm->visible = 1;
            $cm->added = time();
            $cm->id = $DB->insert_record('course_modules', $cm);
            
            course_add_cm_to_section($course, $cm->id, 1);
            echo "    + Created page: {$course_config['page']['name']}\n";
        }
    }
    
    // Create forum
    if (!empty($course_config['forum'])) {
        $forum_exists = $DB->record_exists_sql(
            "SELECT 1 FROM {forum} f JOIN {course_modules} cm ON f.id = cm.instance 
             JOIN {modules} m ON m.id = cm.module 
             WHERE cm.course = ? AND f.name = ? AND m.name = 'forum'",
            [$course->id, $course_config['forum']]
        );
        
        if (!$forum_exists) {
            $module = $DB->get_record('modules', ['name' => 'forum']);
            
            $forum = new stdClass();
            $forum->course = $course->id;
            $forum->name = $course_config['forum'];
            $forum->intro = '<p>Use this forum to discuss course topics and ask questions.</p>';
            $forum->introformat = FORMAT_HTML;
            $forum->type = 'general';
            $forum->timemodified = time();
            $forum->id = $DB->insert_record('forum', $forum);
            
            $cm = new stdClass();
            $cm->course = $course->id;
            $cm->module = $module->id;
            $cm->instance = $forum->id;
            $cm->section = 1;
            $cm->visible = 1;
            $cm->added = time();
            $cm->id = $DB->insert_record('course_modules', $cm);
            
            course_add_cm_to_section($course, $cm->id, 1);
            echo "    + Created forum: {$course_config['forum']}\n";
        }
    }
    
    // Create assignments
    $section = 2;
    foreach ($course_config['assignments'] as $assign_config) {
        $assign_exists = $DB->record_exists_sql(
            "SELECT 1 FROM {assign} a JOIN {course_modules} cm ON a.id = cm.instance 
             JOIN {modules} m ON m.id = cm.module 
             WHERE cm.course = ? AND a.name = ? AND m.name = 'assign'",
            [$course->id, $assign_config['name']]
        );
        
        if (!$assign_exists) {
            $module = $DB->get_record('modules', ['name' => 'assign']);
            
            $assign = new stdClass();
            $assign->course = $course->id;
            $assign->name = $assign_config['name'];
            $assign->intro = $assign_config['intro'];
            $assign->introformat = FORMAT_HTML;
            $assign->alwaysshowdescription = 1;
            $assign->submissiondrafts = 0;
            $assign->sendnotifications = 0;
            $assign->sendlatenotifications = 0;
            $assign->sendstudentnotifications = 1;
            $assign->duedate = time() + (14 * 24 * 60 * 60); // 2 weeks from now
            $assign->cutoffdate = time() + (21 * 24 * 60 * 60); // 3 weeks from now
            $assign->gradingduedate = time() + (28 * 24 * 60 * 60); // 4 weeks from now
            $assign->allowsubmissionsfromdate = time() - (24 * 60 * 60); // Yesterday (open now)
            $assign->grade = $assign_config['grade'];
            $assign->timemodified = time();
            $assign->id = $DB->insert_record('assign', $assign);
            
            // Enable online text submission
            $plugin_config = new stdClass();
            $plugin_config->assignment = $assign->id;
            $plugin_config->plugin = 'onlinetext';
            $plugin_config->subtype = 'assignsubmission';
            $plugin_config->name = 'enabled';
            $plugin_config->value = 1;
            $DB->insert_record('assign_plugin_config', $plugin_config);
            
            // Enable file submission
            $plugin_config = new stdClass();
            $plugin_config->assignment = $assign->id;
            $plugin_config->plugin = 'file';
            $plugin_config->subtype = 'assignsubmission';
            $plugin_config->name = 'enabled';
            $plugin_config->value = 1;
            $DB->insert_record('assign_plugin_config', $plugin_config);
            
            // Set max files
            $plugin_config = new stdClass();
            $plugin_config->assignment = $assign->id;
            $plugin_config->plugin = 'file';
            $plugin_config->subtype = 'assignsubmission';
            $plugin_config->name = 'maxfilesubmissions';
            $plugin_config->value = 5;
            $DB->insert_record('assign_plugin_config', $plugin_config);
            
            // Set max file size (10MB)
            $plugin_config = new stdClass();
            $plugin_config->assignment = $assign->id;
            $plugin_config->plugin = 'file';
            $plugin_config->subtype = 'assignsubmission';
            $plugin_config->name = 'maxsubmissionsizebytes';
            $plugin_config->value = 10485760;
            $DB->insert_record('assign_plugin_config', $plugin_config);
            
            // Enable feedback comments
            $plugin_config = new stdClass();
            $plugin_config->assignment = $assign->id;
            $plugin_config->plugin = 'comments';
            $plugin_config->subtype = 'assignfeedback';
            $plugin_config->name = 'enabled';
            $plugin_config->value = 1;
            $DB->insert_record('assign_plugin_config', $plugin_config);
            
            // Enable feedback files
            $plugin_config = new stdClass();
            $plugin_config->assignment = $assign->id;
            $plugin_config->plugin = 'file';
            $plugin_config->subtype = 'assignfeedback';
            $plugin_config->name = 'enabled';
            $plugin_config->value = 1;
            $DB->insert_record('assign_plugin_config', $plugin_config);
            
            // Create course module
            $cm = new stdClass();
            $cm->course = $course->id;
            $cm->module = $module->id;
            $cm->instance = $assign->id;
            $cm->section = $section;
            $cm->visible = 1;
            $cm->added = time();
            $cm->id = $DB->insert_record('course_modules', $cm);
            
            course_add_cm_to_section($course, $cm->id, $section);
            
            // Create grade item using proper Moodle API
            // This ensures the grade item is properly linked to the course grade category
            $assign->courseid = $course->id;
            $assign->cmidnumber = $cm->id;
            assign_grade_item_update($assign);
            
            echo "    + Created assignment: {$assign_config['name']}\n";
        }
        $section++;
    }
}

// ============================================
// 5. CREATE CREDENTIALS FILE
// ============================================
echo "\nGenerating credentials.txt...\n";

$credentials_content = "================================================================\n";
$credentials_content .= "MOODLE TEST ENVIRONMENT - CREDENTIALS & ENROLLMENT INFO\n";
$credentials_content .= "================================================================\n";
$credentials_content .= "Generated: " . date('Y-m-d H:i:s') . "\n";
$credentials_content .= "Site URL: http://localhost:8080\n";
$credentials_content .= "phpMyAdmin: http://localhost:8081\n";
$credentials_content .= "================================================================\n\n";

// Site Admin
$credentials_content .= "SITE ADMINISTRATOR\n";
$credentials_content .= "----------------------------------------------------------------\n";
$credentials_content .= "Username: admin\n";
$credentials_content .= "Password: Admin@123\n";
$credentials_content .= "Role: Site Administrator (Full Access)\n";
$credentials_content .= "----------------------------------------------------------------\n\n";

// Test Users
$credentials_content .= "TEST USER ACCOUNTS\n";
$credentials_content .= "================================================================\n\n";

foreach ($test_users as $userdata) {
    $username = $userdata['username'];
    $credentials_content .= "USER: {$userdata['firstname']} {$userdata['lastname']}\n";
    $credentials_content .= "----------------------------------------------------------------\n";
    $credentials_content .= "Username: {$username}\n";
    $credentials_content .= "Password: {$userdata['password']}\n";
    $credentials_content .= "Email: {$userdata['email']}\n";
    $credentials_content .= "Role: " . ucfirst($userdata['role']) . "\n";
    
    if (isset($enrollment_data[$username]['courses'])) {
        $credentials_content .= "\nEnrolled Courses:\n";
        foreach ($enrollment_data[$username]['courses'] as $course_info) {
            $credentials_content .= "  - [{$course_info['shortname']}] {$course_info['fullname']} (as {$course_info['role']})\n";
        }
    }
    $credentials_content .= "\n----------------------------------------------------------------\n\n";
}

// Course Summary
$credentials_content .= "COURSE SUMMARY\n";
$credentials_content .= "================================================================\n\n";

foreach ($courses_config as $course_config) {
    $course = $created_courses[$course_config['shortname']] ?? null;
    $course_id = $course ? $course->id : 'N/A';
    
    $credentials_content .= "COURSE: {$course_config['fullname']}\n";
    $credentials_content .= "----------------------------------------------------------------\n";
    $credentials_content .= "Short Name: {$course_config['shortname']}\n";
    $credentials_content .= "Course ID: {$course_id}\n";
    $credentials_content .= "URL: http://localhost:8080/course/view.php?id={$course_id}\n";
    $credentials_content .= "\nTeachers:\n";
    foreach ($course_config['teachers'] as $teacher) {
        $t = $created_users[$teacher];
        $credentials_content .= "  - {$t->firstname} {$t->lastname} ({$teacher})\n";
    }
    $credentials_content .= "\nStudents:\n";
    foreach ($course_config['students'] as $student) {
        $s = $created_users[$student];
        $credentials_content .= "  - {$s->firstname} {$s->lastname} ({$student})\n";
    }
    $credentials_content .= "\nAssignments:\n";
    foreach ($course_config['assignments'] as $idx => $assign) {
        $credentials_content .= "  " . ($idx + 1) . ". {$assign['name']} (Max Grade: {$assign['grade']})\n";
    }
    $credentials_content .= "\n----------------------------------------------------------------\n\n";
}

// Quick Reference
$credentials_content .= "QUICK REFERENCE - LOGIN CREDENTIALS\n";
$credentials_content .= "================================================================\n";
$credentials_content .= "| Username      | Password   | Role           |\n";
$credentials_content .= "----------------------------------------------------------------\n";
$credentials_content .= "| admin         | Admin@123  | Site Admin     |\n";
$credentials_content .= "| testadmin     | Test@1234  | Manager        |\n";
$credentials_content .= "| testteacher   | Test@1234  | Teacher        |\n";
$credentials_content .= "| testteacher2  | Test@1234  | Teacher        |\n";
$credentials_content .= "| teststudent   | Test@1234  | Student        |\n";
$credentials_content .= "| teststudent2  | Test@1234  | Student        |\n";
$credentials_content .= "----------------------------------------------------------------\n\n";

// Test Scenarios
$credentials_content .= "SUGGESTED TEST SCENARIOS\n";
$credentials_content .= "================================================================\n";
$credentials_content .= "1. Login Test: Use teststudent/Test@1234 to test login\n";
$credentials_content .= "2. Course Access: Navigate to CS101 as a student\n";
$credentials_content .= "3. Assignment Submission: Submit text/file to any assignment\n";
$credentials_content .= "4. Teacher Grading: Login as testteacher, grade a submission\n";
$credentials_content .= "5. Forum Post: Create a new discussion in a course forum\n";
$credentials_content .= "6. Profile Edit: Update user profile information\n";
$credentials_content .= "7. Multi-role Test: teststudent is in 4 courses, teststudent2 in 4\n";
$credentials_content .= "================================================================\n";

// Write to file
$credentials_file = $CFG->dirroot . '/credentials.txt';
file_put_contents($credentials_file, $credentials_content);
echo "  + Created credentials.txt\n";

// Also create in moodledata for persistence
$credentials_file_data = $CFG->dataroot . '/credentials.txt';
file_put_contents($credentials_file_data, $credentials_content);

// ============================================
// 6. FINAL SUMMARY
// ============================================
echo "\n==============================================\n";
echo "SETUP COMPLETE!\n";
echo "==============================================\n\n";

echo "USERS CREATED: " . count($test_users) . " test accounts\n";
echo "COURSES CREATED: " . count($courses_config) . " courses\n";
echo "CREDENTIALS FILE: credentials.txt\n\n";

echo "Quick Login Reference:\n";
echo "----------------------------------------------------------------\n";
echo "| Username      | Password   | Role           |\n";
echo "----------------------------------------------------------------\n";
echo "| admin         | Admin@123  | Site Admin     |\n";
echo "| testadmin     | Test@1234  | Manager        |\n";
echo "| testteacher   | Test@1234  | Teacher        |\n";
echo "| testteacher2  | Test@1234  | Teacher        |\n";
echo "| teststudent   | Test@1234  | Student        |\n";
echo "| teststudent2  | Test@1234  | Student        |\n";
echo "----------------------------------------------------------------\n\n";

echo "Enrollment Summary:\n";
echo "- teststudent: CS101, MATH201, ENG102, BUS301 (4 courses)\n";
echo "- teststudent2: CS101, ENG102, PHY101, BUS301 (4 courses)\n";
echo "- testteacher: CS101, MATH201, PHY101, BUS301 (4 courses)\n";
echo "- testteacher2: MATH201, ENG102, BUS301 (3 courses)\n\n";

echo "Ready for testing!\n";
