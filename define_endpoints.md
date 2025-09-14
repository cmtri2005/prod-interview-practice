# DEFINE HTTP ENDPOINT

## Voice Service

'POST voice/upload'

- **Request Body:**
  ```json
  {
    "user_id": "str",
    "file_voice": ""
  }
  ```
- **Response**

## JD Analytic Service

'POST jd/extract'

- **Request Body:**
  ```json
  {
    "jd_content": "str"
  }
  ```
- **Response:**
  ```json
  {
    "job_summary": "str",
    "required_hard_skills": "List[str]",
    "optional_hard_skills": "List[str]",
    "required_soft_skills": "List[str]",
    "optional_soft_skills": "List[str]",
    "required_work_experiences": {
        [
            "job_title": "str",
            "company": "str",
            "dates": "str",
            "responsibilities": "List[str]"
        ]
    },
    "optional_work_experiences": {
        [
            "job_title": "str",
            "company": "str",
            "dates": "str",
            "responsibilities": "List[str]"
        ]
    },
    "required_educations": "List[str]",
    "optional_educations": "List[str]",
    "required_years_of_experience": "int"
  }
  ```

## Resume Analytic Service

'POST resume/extract'

- **Request Body:**
  ```json
  {
    "resume_content": "str"
  }
  ```
- **Response:**
  ```json
  {
    "profile_summary": "str",
    "hard_skills": "List[str]",
    "soft_skills": "List[str]",
    "work_experiences": {
        [
            "job_title": "str",
            "company": "str",
            "dates": "str",
            "responsibilities": "List[str]"
        ]
    },
    "educations": "List[str]",
    "years_of_experience": "int",
    "certifications": "List[str]",
    "projects": "List[str]"
  }
  ```

## JD-Resume Comparison Service

## Resume Review Service

## Interview Service

## Interview Review Service

## Job Recommendation Service

## Proctor Service
