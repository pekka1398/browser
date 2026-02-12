
import json
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_contents(contents: List[Dict]) -> List[Dict]:
    """Clean course contents section."""
    cleaned_data = []
    
    for section in contents:
        clean_section = {
            "name": section.get("name", "Unknown Section"),
            "modules": []
        }
        
        for module in section.get("modules", []):
            clean_module = {
                "name": module.get("name"),
                "type": module.get("modname"),
                "url": module.get("url")
            }
            
            # If it's a file resource, keep file info
            if "contents" in module:
                files = []
                for f in module["contents"]:
                    if f.get("type") == "file":
                        files.append({
                            "filename": f.get("filename"),
                            "fileurl": f.get("fileurl")
                        })
                if files:
                    clean_module["files"] = files
            
            clean_section["modules"].append(clean_module)
            
        cleaned_data.append(clean_section)
    
    return cleaned_data

def clean_assignments(assignments: List[Dict]) -> List[Dict]:
    """Clean assignments section, extracting key submission details."""
    cleaned_data = []
    
    for assign in assignments:
        clean_assign = {
            "name": assign.get("name"),
            "duedate": assign.get("duedate"),
            "intro": assign.get("intro")  # Keep intro (HTML)
        }
        
        # Simplify submission details
        sub_details = assign.get("submission_details", {})
        if "lastattempt" in sub_details:
            attempt = sub_details["lastattempt"]
            submission = attempt.get("submission", {})
            
            clean_sub = {
                "status": submission.get("status"),
                "timecreated": submission.get("timecreated"),
                "timemodified": submission.get("timemodified"),
                "submitted_files": []
            }

            # Extract submitted files
            for plugin in submission.get("plugins", []):
                if plugin.get("type") == "file":
                    for filearea in plugin.get("fileareas", []):
                        for f in filearea.get("files", []):
                            clean_sub["submitted_files"].append({
                                "filename": f.get("filename"),
                                "fileurl": f.get("fileurl"),
                                "timemodified": f.get("timemodified")
                            })
            
            clean_assign["submission"] = clean_sub
            
            # Extract Grade/Feedback
            feedback = sub_details.get("feedback", {})
            if "grade" in feedback:
                grade_info = feedback["grade"]
                clean_assign["evaluation"] = {
                    "grade": grade_info.get("grade"),
                    "gradeddate": feedback.get("gradeddate"),
                    "gradefordisplay": feedback.get("gradefordisplay")
                }
                
                # Feedback comments
                for plugin in feedback.get("plugins", []):
                    if plugin.get("type") == "comments":
                        for field in plugin.get("editorfields", []):
                             if field.get("text"):
                                 clean_assign["evaluation"]["comment"] = field.get("text")


        cleaned_data.append(clean_assign)
        
    return cleaned_data

def clean_forums(forums: List[Dict]) -> List[Dict]:
    """Clean forums section."""
    cleaned_data = []
    
    for forum in forums:
        clean_forum = {
            "name": forum.get("name"),
            "type": forum.get("type"),
            "discussions": []
        }
        
        for discussion in forum.get("discussions", []):
            clean_forum["discussions"].append({
                "subject": discussion.get("subject"),
                "author": discussion.get("userfullname"),
                "created": discussion.get("created"),
                "message": discussion.get("message") # Keep full message
            })
            
        cleaned_data.append(clean_forum)
        
    return cleaned_data

def clean_grades(grades: List[Dict]) -> List[Dict]:
    """Clean grades (already quite simple)."""
    # Keep as is, just copy
    return [g.copy() for g in grades]

def main():
    import sys
    import os
    
    # Check for command line argument for Course ID
    if len(sys.argv) > 1:
        COURSE_ID = int(sys.argv[1])
    else:
        COURSE_ID = 48736 

    INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", f"course_{COURSE_ID}_full_data.json")
    OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", f"course_{COURSE_ID}_clean.json")
    
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        logger.info(f"Loaded {len(data)} top-level keys from {INPUT_FILE}")
        
        cleaned_course = {
            "course_id": data.get("course_id"),
            "fetched_at": data.get("fetched_at"),
            "contents": clean_contents(data.get("contents", [])),
            "assignments": clean_assignments(data.get("assignments", [])),
            "grades": clean_grades(data.get("grades", [])),
            "forums": clean_forums(data.get("forums", [])),
            # Optional blocks, pages (if needed)
            "pages": [{"name": p.get("name"), "content": p.get("content")} for p in data.get("pages", [])],
        }
        
        # Save
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_course, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Cleaned data saved to {OUTPUT_FILE}")
        
    except FileNotFoundError:
        logger.error(f"❌ Input file {INPUT_FILE} not found.")
    except Exception as e:
        logger.error(f"❌ Error processing JSON: {e}")

if __name__ == "__main__":
    main()
