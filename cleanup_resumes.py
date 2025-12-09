from resumecreate.models import Resume
from django.contrib.auth.models import User

# Set username here
username = "godwinkamagco@gmail.com"

try:
    user = User.objects.get(username=username)
except User.DoesNotExist:
    print(f"❌ User '{username}' not found. Exiting.")
    exit()

print(f"\n🔍 Found user: {username}")
print("=" * 60)

# STEP 2: Show current drafts
all_drafts = Resume.objects.filter(user=user, status='draft')
print(f"\n📋 You have {all_drafts.count()} draft document(s):")
for i, draft in enumerate(all_drafts, 1):
    conv_count = len(draft.sections.get('conversation', []))
    print(f"  {i}. Title: '{draft.title}' | Messages: {conv_count}")

# STEP 3: DELETE ALL drafts and start fresh
print("\n⚠️ RECOMMENDED: Delete all drafts and create fresh ones")
confirm = input("Type 'DELETE' to confirm: ").strip().upper()

if confirm == 'DELETE':
    all_drafts.delete()
    print("✅ All drafts deleted!")

    # Create clean resume draft
    Resume.objects.create(
        user=user,
        status='draft',
        title='New Resume',
        sections={
            'type': 'resume',
            'conversation': [],
            'progress': {'current_step': 1}
        }
    )
    print("✅ Created: New Resume (empty)")

    # Create clean cover letter draft
    Resume.objects.create(
        user=user,
        status='draft',
        title='Cover Letter Draft',
        sections={
            'type': 'cover_letter',
            'conversation': [],
            'progress': {
                'job_details': False,
                'key_skills': False,
                'experience': False,
                'motivation': False
            }
        }
    )
    print("✅ Created: Cover Letter Draft (empty)")
    print("\n🎉 Done! Now refresh your browser and test both pages.")
else:
    print("❌ Cancelled. No changes made.")

print("=" * 60)
