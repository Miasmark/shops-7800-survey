-- sd_force.lua: run.lua's session, plus
--   FORCE  "frame:pc:addr=val,addr=val;..."  at the end of that frame write the bytes and set the
--          CPU's PC (hex). The PC before the change is logged to force.txt with SP and the stack top,
--          so the run says where the CPU was taken from. This is NOT something the game did: use it
--          only to enter a routine whose natural trigger was not reached, and say so.
--   PCLOG  "from-to"  log the PC at each frame end in that window (force.txt), to see where the
--          main program waits.
--   XT     "1" also run the toolkit's exectrace.lua (exectrace.log; set A7800_XT_LOWBANK=6)
local here = os.getenv("SD_TOOLS")
dofile(here .. "/run.lua")
local M2 = manager.machine
local cpu2 = M2.devices[":maincpu"]
local mem2 = cpu2.spaces["program"]
local forces = {}
for fr, pc, list in string.gmatch(os.getenv("FORCE") or "", "(%d+):(%x+):([^;]*)") do
  local t = {pc = tonumber(pc, 16), w = {}}
  for ad, val in string.gmatch(list, "(%x+)=(%x+)") do t.w[#t.w + 1] = {tonumber(ad, 16), tonumber(val, 16)} end
  forces[tonumber(fr)] = t
end
local la, lb = string.match(os.getenv("PCLOG") or "", "(%d+)%-(%d+)")
la, lb = tonumber(la or "0"), tonumber(lb or "-1")
local fo = io.open("force.txt", "w")
local ff = 0
local function st()
  local sp = cpu2.state["SP"].value & 0xFF
  local s = {}
  for i = 1, 8 do s[#s + 1] = string.format("%02X", mem2:read_u8(0x100 + ((sp + i) & 0xFF))) end
  return string.format("PC=%04X SP=%02X stack=%s", cpu2.state["PC"].value, sp, table.concat(s, " "))
end
SDF = emu.register_frame_done(function()
  ff = ff + 1
  if ff >= la and ff <= lb then fo:write(string.format("%d %s\n", ff, st())) fo:flush() end
  local t = forces[ff]
  if t then
    fo:write(string.format("%d FORCE from %s to %04X\n", ff, st(), t.pc))
    for _, w in ipairs(t.w) do mem2:write_u8(w[1], w[2]) end
    cpu2.state["PC"].value = t.pc
    fo:flush()
  end
end)
if os.getenv("XT") then
  dofile(here .. "/../../../a7800-toolkit/probes/exectrace.lua")
end
