from flask import Flask, render_template, request, jsonify
from flask import Flask, send_from_directory
import os

app = Flask(__name__)


class CurrentValidID:
    def _init_(self):
        self.year = 0
        self.branch = ""
        self.total_voters = 0

class Candidate:
    def _init_(self, cid, cname):
        self.cid = cid      # Candidate ID
        self.cname = cname  # Candidate Name
        self.votes = 0      # Initialize votes to 0

# GLOBALS -----------------------------------------------
current_valid_id = CurrentValidID()
candidate_array = []
number_of_candidates = 0
student_votes = ['0'] * 200
banned_users = set()  # Set to keep track of banned user IDs
# ------------------------------------------------------


def extract_year(user_id):
    return int(user_id[:4])

def extract_roll_no(user_id):
    return int(user_id[9:14])

def check_branch_code(user_id):
    branch_code = user_id[4:9]
    return branch_code == current_valid_id.branch

def create_candidate_files():
    for i in range(number_of_candidates):
        filename = f"candidate{i + 1}.txt"
        with open(filename, "w") as fp:
            fp.write(f"0\n{candidate_array[i].cname}\n")

def save_election_info_in_file():
    with open("ElectionInfo.txt", "w") as fp:
        fp.write(f"{current_valid_id.year}\n{current_valid_id.branch}\n{current_valid_id.total_voters}\n{number_of_candidates}\n")



@app.route('/')
def home():
       return render_template('index.html')

@app.route('/admin/authenticate', methods=['POST'])
def authenticate_admin():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    if username == "Project12" and password == "NIMIT":
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 401

@app.route('/student/validate', methods=['POST'])
def is_valid():
    user_id = request.json.get("user_id")
    if len(user_id) != 14:
        return jsonify({"valid": False}), 200
    
    inputed_year = extract_year(user_id)
    inputed_roll_no = extract_roll_no(user_id)
    
    if inputed_year != current_valid_id.year or not check_branch_code(user_id) or inputed_roll_no > current_valid_id.total_voters:
        return jsonify({"valid": False}), 200

    return jsonify({"valid": True}), 200

@app.route('/vote', methods=['POST'])
def save_vote():
    data = request.json
    user_id = data.get("user_id")
    vote_input = data.get("vote_input")
    
    filename = f"candidate{int(vote_input)}.txt"
    location = extract_roll_no(user_id)
    
    if student_votes[location - 1] != '0':
        return jsonify({"message": "User has already voted."}), 400
    
    student_votes[location - 1] = vote_input

    candidate_index = int(vote_input) - 1
    candidate_array[candidate_index].votes += 1

    with open(filename, "r+") as fp:
        lines = fp.readlines()
        lines[0] = f"{candidate_array[candidate_index].votes}\n"  # Update votes in the file
        fp.seek(0)
        fp.writelines(lines)
        fp.write(f"{location}\n")  # Save the vote location

    return jsonify({"message": "Vote saved successfully"}), 200

@app.route('/admin/initiate', methods=['POST'])
def initiate_new_election():
    global number_of_candidates
    data = request.json
    current_valid_id.year = data.get("year")
    current_valid_id.branch = data.get("branch")
    current_valid_id.total_voters = data.get("total_voters")
    
    number_of_candidates = data.get("number_of_candidates")
    global student_votes
    student_votes = ['0'] * current_valid_id.total_voters

    for i in range(number_of_candidates):
        cname = data.get(f"candidate_{i + 1}")
        candidate_array.append(Candidate(i + 1, cname))

    save_election_info_in_file()
    create_candidate_files()
    return jsonify({"message": "New election initiated successfully"}), 200

@app.route('/admin/continue', methods=['POST'])
def continue_election():
    # Logic to continue the previous election, 
    # such as loading previous election settings or resetting votes.
    try:
        # You can add logic here to check the current election status
        if current_valid_id.year == 0:
            return jsonify({"message": "No election has been initiated."}), 400

        # If you have specific logic to continue, implement it here
        return jsonify({"message": "Election continued successfully."}), 200
    except Exception as e:
        return jsonify({"message": "Error continuing the election: " + str(e)}), 500

@app.route('/admin/ban', methods=['POST'])
def ban_user():
    user_id = request.json.get("user_id")
    if user_id not in banned_users:
        banned_users.add(user_id)
        return jsonify({"message": f"User ID {user_id} has been banned."}), 200
    return jsonify({"message": f"User ID {user_id} is already banned."}), 400



@app.route('/delete_vote', methods=['POST'])
def delete_vote():
    data = request.json
    user_id = data.get("user_id")
    
    location = extract_roll_no(user_id)
    
    if student_votes[location - 1] == '0':
        return jsonify({"message": "This user has not voted yet."}), 400
    
    if student_votes[location - 1] == '$':
        return jsonify({"message": "This user ID is banned and cannot delete a vote."}), 403

    # Get the candidate ID from the student_votes
    candidate_index = int(student_votes[location - 1]) - 1  # Adjusted to match candidate index
    filename = f"candidate{candidate_array[candidate_index].cid}.txt"
    
    candidate_array[candidate_index].votes -= 1
    student_votes[location - 1] = '0'  # Reset the vote for the user

    if not os.path.exists(filename):
        return jsonify({"message": "File cannot be opened... Operation Failed"}), 500

    # Read file, update votes, and write back
    with open(filename, "r") as fp:
        lines = fp.readlines()

    with open("tmp.txt", "w") as fcp:
        for line in lines:
            fcp.write(line)

    with open(filename, "w") as fp:
        num_from_file = int(lines[0].strip())
        fp.write(f"{num_from_file - 1}\n{lines[1].strip()}\n")
        for line in lines[2:]:
            num = int(line.strip())
            if num != location:
                fp.write(f"{num}\n")

    os.remove("tmp.txt")
    return jsonify({"message": "Vote deleted successfully"}), 200


@app.route('/results', methods=['GET'])
def display_results():
    total_voted_now = sum(candidate.votes for candidate in candidate_array)
    results = [{"id": candidate.cid, "name": candidate.cname, "votes": candidate.votes} for candidate in candidate_array]
    voting_percentage = int((total_voted_now * 100) / current_valid_id.total_voters) if current_valid_id.total_voters > 0 else 0
    return jsonify({"results": results, "voting_percentage": voting_percentage}), 200



if __name__ == '__main__':
    app.run(debug=True)