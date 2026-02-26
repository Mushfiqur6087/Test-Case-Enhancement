#!/bin/bash
set -e

# Wait for database to be ready using PHP (mysqladmin not available in php:apache image)
echo "Waiting for database connection..."
max_tries=60
counter=0

wait_for_db() {
    php -r "
    \$host = getenv('MOODLE_DATABASE_HOST') ?: 'localhost';
    \$user = getenv('MOODLE_DATABASE_USER') ?: 'moodle';
    \$pass = getenv('MOODLE_DATABASE_PASSWORD') ?: 'moodle';
    \$port = getenv('MOODLE_DATABASE_PORT') ?: '3306';
    
    \$conn = @new mysqli(\$host, \$user, \$pass, '', (int)\$port);
    if (\$conn->connect_error) {
        exit(1);
    }
    \$conn->close();
    exit(0);
    " 2>/dev/null
}

while ! wait_for_db; do
    counter=$((counter + 1))
    if [ $counter -gt $max_tries ]; then
        echo "Error: Database connection failed after $max_tries attempts"
        exit 1
    fi
    echo "Waiting for database... ($counter/$max_tries)"
    sleep 2
done
echo "Database is ready!"

CONFIG_FILE="/var/www/html/config.php"

# Create config.php if it doesn't exist
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating Moodle config.php..."
    cat > "$CONFIG_FILE" << EOF
<?php
unset(\$CFG);
global \$CFG;
\$CFG = new stdClass();

// Database settings
\$CFG->dbtype    = '${MOODLE_DATABASE_TYPE:-mysqli}';
\$CFG->dblibrary = 'native';
\$CFG->dbhost    = '${MOODLE_DATABASE_HOST:-localhost}';
\$CFG->dbname    = '${MOODLE_DATABASE_NAME:-moodle}';
\$CFG->dbuser    = '${MOODLE_DATABASE_USER:-moodle}';
\$CFG->dbpass    = '${MOODLE_DATABASE_PASSWORD:-moodle}';
\$CFG->prefix    = 'mdl_';
\$CFG->dboptions = array(
    'dbpersist' => false,
    'dbsocket'  => false,
    'dbport'    => '${MOODLE_DATABASE_PORT:-3306}',
    'dbcollation' => 'utf8mb4_unicode_ci',
);

// Site settings
\$CFG->wwwroot   = '${MOODLE_WWWROOT:-http://localhost:8080}';
\$CFG->dataroot  = '${MOODLE_DATAROOT:-/var/www/moodledata}';
\$CFG->admin     = 'admin';

// Directory permissions
\$CFG->directorypermissions = 02777;

// Debug settings (for testing)
\$CFG->debug = E_ALL | E_STRICT;
\$CFG->debugdisplay = 1;
\$CFG->debugdeveloper = true;

// Performance settings for testing
\$CFG->cachejs = false;
\$CFG->langstringcache = false;

// Enable test data generator
\$CFG->tool_generator_users_password = 'Testing@123';

require_once(__DIR__ . '/public/lib/setup.php');
EOF
    chown www-data:www-data "$CONFIG_FILE"
    echo "Config file created successfully!"
fi

# Check if Moodle is already installed using PHP
INSTALL_CHECK=$(php -r "
\$host = getenv('MOODLE_DATABASE_HOST') ?: 'localhost';
\$user = getenv('MOODLE_DATABASE_USER') ?: 'moodle';
\$pass = getenv('MOODLE_DATABASE_PASSWORD') ?: 'moodle';
\$db   = getenv('MOODLE_DATABASE_NAME') ?: 'moodle';
\$port = getenv('MOODLE_DATABASE_PORT') ?: '3306';

\$conn = new mysqli(\$host, \$user, \$pass, \$db, (int)\$port);
if (\$conn->connect_error) {
    echo '0';
    exit;
}
\$result = \$conn->query(\"SHOW TABLES LIKE 'mdl_config'\");
echo \$result->num_rows > 0 ? '1' : '0';
\$conn->close();
" 2>/dev/null || echo "0")

if [ "$INSTALL_CHECK" = "0" ]; then
    echo "Installing Moodle..."
    
    # Run Moodle CLI installer
    php /var/www/html/admin/cli/install_database.php \
        --agree-license \
        --adminuser="${MOODLE_ADMIN_USER:-admin}" \
        --adminpass="${MOODLE_ADMIN_PASSWORD:-Admin@123}" \
        --adminemail="${MOODLE_ADMIN_EMAIL:-admin@example.com}" \
        --fullname="${MOODLE_SITE_NAME:-Moodle Test Site}" \
        --shortname="MoodleTest"
    
    echo "Moodle installed successfully!"
    
    # Run custom test data setup script
    echo "Setting up test accounts and course..."
    php /var/www/html/setup-test-data.php || echo "Custom test data setup completed"
    
    # Generate additional test data if enabled
    if [ "${MOODLE_GENERATE_TEST_DATA:-false}" = "true" ]; then
        echo "Generating additional test data (size: ${MOODLE_TEST_DATA_SIZE:-S})..."
        echo "This may take a few minutes depending on the size selected..."
        
        php /var/www/html/public/admin/tool/generator/cli/maketestsite.php \
            --size="${MOODLE_TEST_DATA_SIZE:-S}" \
            --bypasscheck \
            --fixeddataset || echo "Test data generation completed (some warnings may be normal)"
        
        echo "Test data generated successfully!"
    fi
else
    echo "Moodle is already installed, skipping installation..."
    
    # Run any pending upgrades
    echo "Checking for upgrades..."
    php /var/www/html/admin/cli/upgrade.php --non-interactive || true
fi

# Ensure correct permissions
chown -R www-data:www-data /var/www/moodledata
chmod -R 755 /var/www/moodledata

# Copy credentials.txt to web-accessible location if it exists
if [ -f "/var/www/html/credentials.txt" ]; then
    echo ""
    echo "=============================================="
    echo "CREDENTIALS FILE AVAILABLE"
    echo "=============================================="
    cat /var/www/html/credentials.txt | head -40
    echo ""
    echo "(See full file at /var/www/html/credentials.txt)"
    echo "=============================================="
fi

echo ""
echo "=============================================="
echo "Moodle is ready for testing!"
echo "=============================================="
echo ""
echo "SITE URL: ${MOODLE_WWWROOT:-http://localhost:8080}"
echo "phpMyAdmin: http://localhost:8081"
echo ""
echo "ADMIN ACCOUNT:"
echo "  Username: ${MOODLE_ADMIN_USER:-admin}"
echo "  Password: ${MOODLE_ADMIN_PASSWORD:-Admin@123}"
echo ""
echo "TEST ACCOUNTS (Password: Test@1234):"
echo "  testadmin     - Manager role"
echo "  testteacher   - Teacher role (CS101, MATH201, PHY101, BUS301)"
echo "  testteacher2  - Teacher role (MATH201, ENG102, BUS301)"
echo "  teststudent   - Student role (CS101, MATH201, ENG102, BUS301)"
echo "  teststudent2  - Student role (CS101, ENG102, PHY101, BUS301)"
echo ""
echo "TEST COURSES:"
echo "  CS101   - Introduction to Computer Science"
echo "  MATH201 - Calculus I"
echo "  ENG102  - English Composition"
echo "  PHY101  - Physics for Beginners"
echo "  BUS301  - Business Management Fundamentals"
echo ""
echo "CREDENTIALS FILE: credentials.txt (in project root)"
echo "=============================================="
echo ""

# Execute the main command (Apache)
exec "$@"
