-- sd_xt.lua: run.lua's scripted session plus the toolkit's exectrace.lua (exectrace.log in the run folder)
local here = os.getenv("SD_TOOLS")
dofile(here .. "/run.lua")
dofile(here .. "/../../../a7800-toolkit/probes/exectrace.lua")
