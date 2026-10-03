import os
import uuid
import time
import random
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from PIL import Image
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# Load .env
load_dotenv(BASE_DIR / ".env")


# ============================================================
# UPLOAD CONFIGURATION
# ============================================================

UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp",
}


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GOOGLE_GEMINI_API_KEY not found in .env file."
    )

# Don't print the complete API key
print("Gemini API key loaded successfully.")

client = genai.Client(api_key=API_KEY)

# Primary model
MODEL_NAME = "gemini-2.5-flash"

# Fallback model
FALLBACK_MODEL = "gemini-2.5-flash-lite"


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

app.secret_key = os.getenv(
    "FLASK_SECRET",
    "secret-key"
)


# ============================================================
# LOGIN DETAILS
# ============================================================

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin123"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def allowed_file(filename):
    """
    Check whether uploaded file has a supported extension.
    """

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def save_upload_file(file_storage):
    """
    Save uploaded image with a unique filename.
    """

    original_filename = file_storage.filename

    extension = (
        original_filename
        .rsplit(".", 1)[1]
        .lower()
    )

    filename = (
        f"{uuid.uuid4().hex}.{extension}"
    )

    filepath = UPLOAD_FOLDER / filename

    file_storage.save(filepath)

    return filename, filepath


# ============================================================
# GEMINI IMAGE ANALYSIS
# ============================================================

def analyze_image(image):
    """
    Analyze uploaded image using Gemini.

    Includes:
    - Retry mechanism for 503 errors
    - Exponential backoff
    - Fallback model
    """

    prompt = """
Analyze the uploaded image carefully.

Return ONLY the following fields:

Object:
Category:
Summary:
Confidence:
Colors:
Mood:
Social Media Profiles:

Rules:

Object = detected object or person's name.

Category must be one of:
Public Figure,
Person,
Animal,
Vehicle,
Food,
Building,
Document,
Nature,
Electronics.

Summary = a brief description of the image.
Keep it under 100 words.

Confidence = High, Medium, or Low.

Colors = comma-separated list of dominant colors.

Mood = one short phrase describing the atmosphere,
expression, or visual mood.

Social Media Profiles =
Only provide a profile if the identity is confidently
known and the profile is an official public profile.
Otherwise write N/A.

Do not guess a person's identity.

Do not invent social media accounts.

Do not use markdown.

Do not use numbering.

Do not add explanations.

Return ONLY these fields.
"""

    # Models to try
    models_to_try = [
        MODEL_NAME,
        FALLBACK_MODEL,
    ]

    last_error = None

    # ========================================================
    # TRY EACH MODEL
    # ========================================================

    for model_name in models_to_try:

        print()
        print("=" * 60)
        print(f"Using Gemini model: {model_name}")
        print("=" * 60)

        # ====================================================
        # RETRY EACH MODEL 3 TIMES
        # ====================================================

        for attempt in range(3):

            try:

                print(
                    f"Attempt {attempt + 1}/3..."
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=[
                        prompt,
                        image,
                    ],
                )

                # --------------------------------------------
                # Check response
                # --------------------------------------------

                if response is None:
                    raise RuntimeError(
                        "Gemini returned no response."
                    )

                if not response.text:
                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )

                # --------------------------------------------
                # SUCCESS
                # --------------------------------------------

                print(
                    f"SUCCESS: {model_name}"
                )

                print()
                print("Gemini Output:")
                print(response.text)
                print()

                return response.text

            except Exception as e:

                last_error = e

                error_text = str(e)

                print()
                print(
                    f"Gemini error: {error_text}"
                )

                # =================================================
                # HANDLE TEMPORARY 503 ERROR
                # =================================================

                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                ):

                    # Retry if attempts remain
                    if attempt < 2:

                        delay = (
                            (2 ** attempt)
                            + random.uniform(0.5, 1.5)
                        )

                        print(
                            f"Temporary Gemini error."
                        )

                        print(
                            f"Retrying in "
                            f"{delay:.1f} seconds..."
                        )

                        time.sleep(delay)

                        continue

                    # All retries for this model failed
                    print(
                        f"{model_name} is unavailable."
                    )

                    print(
                        "Trying fallback model..."
                    )

                    break

                # =================================================
                # OTHER ERRORS
                # =================================================

                raise

    # ========================================================
    # ALL MODELS FAILED
    # ========================================================

    raise RuntimeError(
        "Gemini image analysis failed after all retries. "
        f"Last error: {last_error}"
    )


# ============================================================
# UPLOAD ROUTE
# ============================================================

@app.route("/upload", methods=["POST"])
def upload():

    # --------------------------------------------------------
    # Login check
    # --------------------------------------------------------

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )

    # --------------------------------------------------------
    # Get uploaded image
    # --------------------------------------------------------

    uploaded_file = request.files.get(
        "imageFile"
    )

    # --------------------------------------------------------
    # No file
    # --------------------------------------------------------

    if (
        uploaded_file is None
        or uploaded_file.filename == ""
    ):

        flash(
            "Please upload an image.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if not allowed_file(
        uploaded_file.filename
    ):

        flash(
            "Unsupported image format. "
            "Use JPG, JPEG, PNG, or WEBP.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # --------------------------------------------------------
    # Save image
    # --------------------------------------------------------

    try:

        filename, filepath = save_upload_file(
            uploaded_file
        )

    except Exception as e:

        print(
            "File save error:",
            repr(e)
        )

        flash(
            "Could not save the uploaded image.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # ========================================================
    # ANALYZE IMAGE
    # ========================================================

    try:

        # Open image
        image = Image.open(filepath)

        # Verify image
        image.verify()

        # Reopen after verify
        image = Image.open(filepath)

        # Gemini analysis
        analysis = analyze_image(
            image
        )

        # ----------------------------------------------------
        # Default values
        # ----------------------------------------------------

        object_name = "Unknown"
        confidence = "N/A"
        category = "Unknown"
        summary = ""
        colors = ""
        mood = ""
        social_media_profiles = "N/A"

        # ----------------------------------------------------
        # Parse Gemini response
        # ----------------------------------------------------

        for line in analysis.splitlines():

            line = line.strip()

            if line.startswith("Object:"):

                object_name = (
                    line
                    .replace("Object:", "", 1)
                    .strip()
                )

            elif line.startswith("Confidence:"):

                confidence = (
                    line
                    .replace("Confidence:", "", 1)
                    .strip()
                )

            elif line.startswith("Category:"):

                category = (
                    line
                    .replace("Category:", "", 1)
                    .strip()
                )

            elif line.startswith("Summary:"):

                summary = (
                    line
                    .replace("Summary:", "", 1)
                    .strip()
                )

            elif line.startswith("Colors:"):

                colors = (
                    line
                    .replace("Colors:", "", 1)
                    .strip()
                )

            elif line.startswith("Mood:"):

                mood = (
                    line
                    .replace("Mood:", "", 1)
                    .strip()
                )

            elif line.startswith(
                "Social Media Profiles:"
            ):

                social_media_profiles = (
                    line
                    .replace(
                        "Social Media Profiles:",
                        "",
                        1
                    )
                    .strip()
                )

    # ========================================================
    # ANALYSIS ERROR
    # ========================================================

    except Exception as e:

        print()
        print("=" * 60)
        print("FINAL IMAGE ANALYSIS ERROR")
        print("=" * 60)
        print(repr(e))
        print("=" * 60)
        print()

        flash(
            "Image analysis is temporarily unavailable. "
            "Please try again in a few seconds.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    # ========================================================
    # SHOW RESULT
    # ========================================================

    return render_template(
        "result.html",

        image_url=url_for(
            "uploaded_file",
            filename=filename
        ),

        analysis=analysis,

        object_name=object_name,

        confidence=confidence,

        category=category,

        summary=summary,

        colors=colors,

        mood=mood,

        social_media_profiles=(
            social_media_profiles
        ),
    )


# ============================================================
# ROOT
# ============================================================

@app.route("/")
def root():

    return redirect(
        url_for("home")
    )


# ============================================================
# HOME
# ============================================================

@app.route("/home")
def home():

    return render_template(
        "home.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = request.form.get(
            "username"
        )

        password = request.form.get(
            "password"
        )

        if (
            username == VALID_USERNAME
            and password == VALID_PASSWORD
        ):

            session["logged_in"] = True

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid username or password",
        )

    return render_template(
        "login.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )

    return render_template(
        "dashboard.html"
    )


# ============================================================
# SERVE UPLOADED IMAGES
# ============================================================

@app.route(
    "/uploads/<filename>"
)
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.pop(
        "logged_in",
        None
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("SMART IMAGE ANALYSIS CHATBOT")
    print("=" * 60)
    print("Primary model :", MODEL_NAME)
    print("Fallback model:", FALLBACK_MODEL)
    print("Upload folder :", UPLOAD_FOLDER)
    print("=" * 60)
    print()

    app.run(
        debug=True
    )