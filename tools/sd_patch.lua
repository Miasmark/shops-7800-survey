-- sd_patch.lua: run.lua's session, plus
--   PATCH  "from-to:addr=val,addr=val;..."  while the frame is in from..to, reads of those
--          addresses return val instead of the ROM's byte (a temporary ROM patch through a read
--          tap: the CPU fetches the patched operand). Used to divert one JSR for a frame or two.
--          This is a forced entry, not something the game did: say so where it is used.
--          patch.txt logs each substituted read (frame, PC, addr).
--   SUBST  "from-to:addr:old=new;..."       writes of old to addr become new in that window
--          (e.g. the shop's item byte), logged too.
--   XT     "1" also run the toolkit's exectrace.lua (exectrace.log; set A7800_XT_LOWBANK=6)
local here = os.getenv("SD_TOOLS")
dofile(here .. "/run.lua")
local M2 = manager.machine
local cpu2 = M2.devices[":maincpu"]
local mem2 = cpu2.spaces["program"]
local ff = 0
local po = io.open("patch.txt", "w")
SDP = {}
for a, b, list in string.gmatch(os.getenv("PATCH") or "", "(%d+)%-(%d+):([^;]+)") do
  local from, to = tonumber(a), tonumber(b)
  for ad, val in string.gmatch(list, "(%x+)=(%x+)") do
    local adr, v = tonumber(ad, 16), tonumber(val, 16)
    SDP[#SDP + 1] = mem2:install_read_tap(adr, adr, "p" .. ad, function(o, d)
      if ff >= from and ff <= to then
        po:write(string.format("%d read %04X PC=%04X %02X->%02X\n", ff, o, cpu2.state["PC"].value, d, v))
        po:flush()
        return v
      end
      return d
    end)
  end
end
for a, b, ad, old, new in string.gmatch(os.getenv("SUBST") or "", "(%d+)%-(%d+):(%x+):(%x+)=(%x+)") do
  local from, to, adr = tonumber(a), tonumber(b), tonumber(ad, 16)
  local o1, n1 = tonumber(old, 16), tonumber(new, 16)
  SDP[#SDP + 1] = mem2:install_write_tap(adr, adr, "s" .. ad, function(o, d)
    if ff >= from and ff <= to and (d & 0xFF) == o1 then
      po:write(string.format("%d write %04X PC=%04X %02X->%02X\n", ff, o, cpu2.state["PC"].value, d & 0xFF, n1))
      po:flush()
      return n1
    end
    return d
  end)
end
SDPF = emu.register_frame_done(function() ff = ff + 1 end)
if os.getenv("XT") then
  dofile(here .. "/../../../a7800-toolkit/probes/exectrace.lua")
end
