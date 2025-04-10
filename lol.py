import os

try:
    os.remove("tele.session")
except:
    pass
try:
    os.remove("tele.session-journal")
except:
    pass
