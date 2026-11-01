# Reliable Student Records Import & Validation Tool
import json
import os
class StudentRecordError(Exception):
    pass
def validate_record(record):
    if not isinstance(record, dict):
        raise TypeError("Student record must be a dictionary.")
    required_fields = ["student_id", "name", "department", "marks"]
    for field in required_fields:
        if field not in record:
            raise KeyError("Missing required field: " + field)
    student_id = record["student_id"]
    name = record["name"]
    department = record["department"]
    marks = record["marks"]
    if not isinstance(student_id, str) or student_id.strip() == "":
        raise ValueError("Student ID must be a non-empty string.")
    if not isinstance(name, str) or name.strip() == "":
        raise ValueError("Student name must be a non-empty string.")
    if not isinstance(department, str) or department.strip() == "":
        raise ValueError("Department must be a non-empty string.")
    if not isinstance(marks, list):
        raise TypeError("Marks must be stored in a list.")
    if len(marks) != 3:
        raise StudentRecordError(
            "Marks must contain exactly 3 values between 0 and 100."
        )
    for mark in marks:
        if isinstance(mark, bool):
            raise StudentRecordError("Boolean values are not valid marks.")
        if not isinstance(mark, (int, float)):
            raise TypeError("Marks must contain numeric values only.")
        if not 0 <= mark <= 100:
            raise StudentRecordError(
                "Marks must be between 0 and 100."
            )
    return True
def load_input_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise TypeError("Input JSON must contain a list of student records.")
    return data
def process_records(data):
    valid_records = []
    rejected_records = []
    student_ids = set()
    for index, record in enumerate(data, start=1):
        try:
            validate_record(record)
            student_id = record["student_id"]
            # Check duplicate student ID
            if student_id in student_ids:
                raise StudentRecordError(
                    "Duplicate student ID: " + student_id
                )
            student_ids.add(student_id)
            valid_records.append(record)
            print(
                "Accepted:",
                student_id,
                "-",
                record["name"]
            )
        except StudentRecordError as error:
            message = "Rejected record " + str(index) + ": " + str(error)
            print(message)
            rejected_records.append(message)
        except KeyError as error:
            message = (
                "Rejected record " + str(index) +
                ": missing required field " + str(error)
            )
            print(message)
            rejected_records.append(message)
        except TypeError as error:
            message = "Rejected record " + str(index) + ": " + str(error)
            print(message)
            rejected_records.append(message)
        except ValueError as error:
            message = "Rejected record " + str(index) + ": " + str(error)
            print(message)
            rejected_records.append(message)
        except IndexError as error:
            message = "Rejected record " + str(index) + ": " + str(error)
            print(message)
            rejected_records.append(message)
    return valid_records, rejected_records
def save_valid_records(records, output_path):
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)
    print("Valid records saved successfully.")
def write_error_log(errors, log_path):
    with open(log_path, "w", encoding="utf-8") as file:
        if len(errors) == 0:
            file.write("No rejected records.\n")
        else:
            file.writelines(error + "\n" for error in errors)

# Main program
def main():
    default_path = "students_input.json"
    file_path = input(
        "Enter input file path (press Enter for default): "
    )
    if file_path == "":
        file_path = default_path
    output_path = "students_valid.json"
    error_path = "import_errors.txt"
    print("\nImport started:", file_path)
    try:
        data = load_input_file(file_path)
    except FileNotFoundError:
        print("Error: Input file not found.")
        try:
            write_error_log(
                ["Input file not found: " + file_path],
                error_path
            )
        except OSError:
            print("Could not write error log.")
        return
    except PermissionError:
        print("Error: Permission denied while reading input file.")
        try:
            write_error_log(
                ["Permission denied: " + file_path],
                error_path
            )
        except OSError:
            print("Could not write error log.")
        return
    except json.JSONDecodeError as error:
        print("Error: Invalid JSON format.")
        print("Details:", error)
        try:
            write_error_log(
                ["Invalid JSON format: " + str(error)],
                error_path
            )
        except OSError:
            print("Could not write error log.")
        return
    except (TypeError, ValueError) as error:
        print("Input format error:", error)
        try:
            write_error_log(
                ["Input format error: " + str(error)],
                error_path
            )
        except OSError:
            print("Could not write error log.")
        return
    except OSError as error:
        print("File error:", error)
        try:
            write_error_log(
                ["File error: " + str(error)],
                error_path
            )
        except OSError:
            print("Could not write error log.")
        return
    else:
        print("Input file read successfully.")
    finally:
        print("Input reading process finished.")
    valid_records, rejected_records = process_records(data)
    try:
        save_valid_records(valid_records, output_path)
    except OSError as error:
        print("Error while saving valid records:", error)
        return
    try:
        write_error_log(rejected_records, error_path)
    except OSError as error:
        print("Error while writing error log:", error)
        return
    # Final summary
    print("\n===== IMPORT SUMMARY =====")
    print("Accepted records:", len(valid_records))
    print("Rejected records:", len(rejected_records))
    print("Valid output:", os.path.abspath(output_path))
    print("Error log:", os.path.abspath(error_path))
    print("Import completed.")
if __name__ == "__main__":
    main()
