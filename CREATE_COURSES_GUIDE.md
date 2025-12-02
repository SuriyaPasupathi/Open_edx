# Creating Sample Courses in Open edX Studio

This guide explains how to manually create courses in Open edX Studio.

## Prerequisites

1. **Access Studio**: Go to `http://52.52.41.225:18010`
2. **Login**: You need a staff user account (not `studio_worker` which uses OAuth only)
3. **Create Staff User** (if needed):
   ```bash
   cd "/home/suriya-vcw/Desktop/manual build/edx-platform"
   ./create_studio_staff_user.sh
   ```

## Method 1: Create Course via Studio Web Interface

### Step 1: Access Studio
1. Navigate to: `http://52.52.41.225:18010`
2. Login with your staff account

### Step 2: Create New Course
1. Click **"Create New Course"** button (top right)
2. Fill in the course details:
   - **Course Name**: e.g., "Introduction to Python"
   - **Organization**: e.g., "edX" or your organization name
   - **Course Number**: e.g., "CS101" or "PYTHON101"
   - **Course Run**: e.g., "2024" or "T1"
3. Click **"Create"**

### Step 3: Configure Course Settings
1. Go to **Settings** → **Schedule & Details**
   - Set **Course Start Date**
   - Set **Course End Date** (optional)
   - Set **Enrollment Start Date**
   - Set **Enrollment End Date** (optional)
2. Go to **Settings** → **Advanced Settings**
   - Configure course metadata
   - Set course visibility (public/private)

### Step 4: Add Course Content
1. Click **"Content"** tab
2. Click **"Add Section"** to create a new section
3. Click **"Add Subsection"** within a section
4. Click **"Add Unit"** within a subsection
5. Click **"Add Component"** to add:
   - **HTML**: Text content, images, videos
   - **Problem**: Multiple choice, text input, etc.
   - **Video**: Upload or embed videos
   - **Discussion**: Discussion forums
   - **Advanced**: Custom XBlocks

### Step 5: Publish Course
1. Click **"Publish"** button for each component/section
2. Go to **Settings** → **Course Schedule** → **Publish Course**

## Method 2: Create Course via Django Management Command

### Step 1: Access LMS Container
```bash
docker exec -it edx_lms bash
```

### Step 2: Create Course Using Management Command
```bash
python manage.py cms create_course \
    --settings=devstack \
    org C101 \
    --user studio_user
```

**Example:**
```bash
python manage.py cms create_course \
    --settings=devstack \
    edX CS101 2024 \
    --user admin
```

### Step 3: Make Course Visible
```bash
python manage.py cms shell --settings=devstack
```

Then in Python shell:
```python
from xmodule.modulestore.django import modulestore
from xmodule.contentstore.django import contentstore
from xmodule.course_module import CourseDescriptor

# Get course
store = modulestore()
course_key = store.make_course_key('edX', 'CS101', '2024')
course = store.get_course(course_key)

# Make course visible
course.visible_to_staff_only = False
store.update_item(course, 'YOUR_USERNAME')

print(f"Course {course_key} is now visible")
exit()
```

## Method 3: Import Sample Course from GitHub

### Step 1: Download Sample Course
```bash
cd /tmp
git clone https://github.com/edx/edx-demo-course.git
cd edx-demo-course
```

### Step 2: Import Course
```bash
docker exec -it edx_lms bash
cd /tmp/edx-demo-course
python /app/manage.py cms import /tmp/edx-demo-course edX DemoX Demo_Course --settings=devstack
```

## Method 4: Create Course with Sample Content (Script)

Create a script to automate course creation:

```bash
#!/bin/bash
# create_sample_course.sh

ORG="edX"
COURSE_NUMBER="SAMPLE101"
RUN="2024"
USERNAME="admin"

docker exec -it edx_lms bash -c "
python manage.py cms create_course \
    --settings=devstack \
    $ORG $COURSE_NUMBER $RUN \
    --user $USERNAME

python manage.py cms shell --settings=devstack <<PYTHON
from xmodule.modulestore.django import modulestore
from xmodule.contentstore.django import contentstore

store = modulestore()
course_key = store.make_course_key('$ORG', '$COURSE_NUMBER', '$RUN')
course = store.get_course(course_key)

if course:
    # Add sample section
    section = store.create_item('$USERNAME', course.location, 'chapter', 'Sample Chapter')
    
    # Add sample subsection
    subsection = store.create_item('$USERNAME', section.location, 'sequential', 'Sample Subsection')
    
    # Add sample unit
    unit = store.create_item('$USERNAME', subsection.location, 'vertical', 'Sample Unit')
    
    print(f'Course created: {course_key}')
    print(f'Section: {section.location}')
    print(f'Subsection: {subsection.location}')
    print(f'Unit: {unit.location}')
else:
    print('Failed to create course')
PYTHON
"
```

## Quick Sample Course Creation Commands

### Create a Simple Course
```bash
docker exec -it edx_lms bash -c "
python manage.py cms create_course \
    --settings=devstack \
    edX DEMO101 2024 \
    --user admin
"
```

### List All Courses
```bash
docker exec -it edx_lms bash -c "
python manage.py cms shell --settings=devstack <<PYTHON
from xmodule.modulestore.django import modulestore
store = modulestore()
courses = store.get_courses()
for course in courses:
    print(f'{course.id}: {course.display_name}')
PYTHON
"
```

### Delete a Course
```bash
docker exec -it edx_lms bash -c "
python manage.py cms delete_course \
    --settings=devstack \
    edX DEMO101 2024 \
    --user admin
"
```

## Common Course Components

### 1. HTML Component (Text Content)
- Click **"Add Component"** → **"HTML"**
- Enter text, HTML, or markdown
- Use rich text editor or raw HTML

### 2. Problem Component (Quiz)
- Click **"Add Component"** → **"Problem"**
- Choose problem type:
  - **Multiple Choice**
  - **Checkboxes**
  - **Text Input**
  - **Numerical Input**
  - **Dropdown**

### 3. Video Component
- Click **"Add Component"** → **"Video"**
- Upload video file or embed from YouTube/Vimeo
- Add transcripts and captions

### 4. Discussion Component
- Click **"Add Component"** → **"Discussion"**
- Configure discussion topic
- Set visibility and permissions

## Course Structure Example

```
Course: Introduction to Python
├── Section 1: Getting Started
│   ├── Subsection 1.1: Installation
│   │   ├── Unit 1.1.1: Overview (HTML)
│   │   ├── Unit 1.1.2: Installation Steps (HTML)
│   │   └── Unit 1.1.3: Check Your Installation (Problem)
│   └── Subsection 1.2: First Program
│       ├── Unit 1.2.1: Hello World (HTML)
│       └── Unit 1.2.2: Practice Exercise (Problem)
├── Section 2: Variables and Data Types
│   ├── Subsection 2.1: Variables
│   └── Subsection 2.2: Data Types
└── Section 3: Control Flow
    ├── Subsection 3.1: If Statements
    └── Subsection 3.2: Loops
```

## Troubleshooting

### Course Not Visible
- Check **Settings** → **Advanced Settings** → **Course Visibility**
- Ensure course is published
- Check user has staff permissions

### Cannot Access Studio
- Verify user is staff: `is_staff = True`
- Check CMS container is running: `docker ps | grep cms`
- Verify Studio URL: `http://52.52.41.225:18010`

### Import Errors
- Ensure course XML is valid
- Check file permissions
- Verify course key format: `org/course_number/run`

## Next Steps

1. **Create Course Content**: Add sections, subsections, and units
2. **Add Problems**: Create quizzes and assignments
3. **Configure Settings**: Set dates, visibility, and metadata
4. **Publish Course**: Make it available to learners
5. **Test Course**: Enroll as a student and test the course flow

## Additional Resources

- [Open edX Studio Documentation](https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/)
- [Course Authoring Guide](https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/course_introduction/index.html)
- [XBlock Development](https://xblock.readthedocs.io/)

