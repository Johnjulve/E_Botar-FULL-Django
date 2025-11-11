from django.contrib import admin

# This project is transitioning from legacy `voting` models to modular apps
# (`election_management`, `candidates`, `votes`, `users`). To avoid duplicate
# sections in Django Admin, we intentionally DO NOT register the legacy
# `voting` models here. The canonical admin registrations live in:
#   - election_management.admin (positions, elections, parties)
#   - candidates.admin (candidates, applications)
#   - votes.admin (school votes, vote receipts)
#   - users.admin (activity logs, profiles)

# If you still need to inspect legacy models via admin during migration,
# you can temporarily re-enable registrations here.
