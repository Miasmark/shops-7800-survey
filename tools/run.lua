-- run.lua: one scripted windowless session (shops-7800-survey). Environment:
--   SCRIPT  "frames:stick:button;..."  stick = letters of l r u d or -, button 0-3 (+4 pause, +8 select, +16 reset)
--   SNAPS   "f1,f2,..."  frames to screenshot
--   END     last frame
--   POKES   "frame:addr=val,addr=val;frame:..."   hex addr/val, written at the end of that frame
--   HOLD    "from-to:addr=val,addr=val;..."      hex addr/val written every frame in the window
--   PEEK    "addr,addr"  hex; frames.txt gets a line per frame where any changed
--   DUMPS   "f1,f2"  frames at which to dump the 64K the CPU sees (dump_fNNNNN.bin) and MARIA writes of that frame
--   WTAP    "lo-hi,lo-hi" hex write taps -> wtap.txt (frame bank PC addr val), frames WFROM..WTO, max WMAX lines
--   RTAP    "lo-hi,..." hex read taps -> rtap.txt distinct (bank PC -> lo..hi of addresses read, count), frames RFROM..RTO
--   EXEC    "1" -> exec.txt: distinct instruction addresses fetched (bank:PC) in frames XFROM..XTO
local M = manager.machine
local cpu = M.devices[":maincpu"]
local mem = cpu.spaces["program"]
local P = M.ioport.ports
local function fld(n)
  for _, t in ipairs({":JOYSTICKS", ":BUTTONS", ":joysticks", ":buttons"}) do
    local f = P[t] and P[t].fields[n]
    if f then return f end
  end
end
local stick = {l = fld("P1 Left"), r = fld("P1 Right"), u = fld("P1 Up"), d = fld("P1 Down")}
local fire = fld("P1 Button 1")
local fire2 = fld("P1 Button 2")
local pause, select, reset
for _, t in ipairs({":CONSOLE", ":console", ":console_buttons"}) do
  if P[t] and P[t].fields["Pause"] then pause = P[t].fields["Pause"] end
  if P[t] and P[t].fields["Select"] then select = P[t].fields["Select"] end
  if P[t] and P[t].fields["Reset"] then reset = P[t].fields["Reset"] end
end
local steps = {}
for n, s, b in string.gmatch(os.getenv("SCRIPT") or "60:-:0", "(%d+):([lrud%-]+):(%d+)") do
  steps[#steps + 1] = {tonumber(n), s, tonumber(b)}
end
local total = 0
for _, s in ipairs(steps) do total = total + s[1] end
local function set(env)
  local t = {}
  for w in string.gmatch(os.getenv(env) or "", "%d+") do t[tonumber(w)] = true end
  return t
end
local snaps, dumps = set("SNAPS"), set("DUMPS")
local END = tonumber(os.getenv("END") or tostring(total))
local pokes = {}
for fr, list in string.gmatch(os.getenv("POKES") or "", "(%d+):([^;]+)") do
  local t = pokes[tonumber(fr)] or {}
  for ad, val in string.gmatch(list, "(%x+)=(%x+)") do t[#t + 1] = {tonumber(ad, 16), tonumber(val, 16)} end
  pokes[tonumber(fr)] = t
end
local holds = {}
for a, b, list in string.gmatch(os.getenv("HOLD") or "", "(%d+)%-(%d+):([^;]+)") do
  local t = {from = tonumber(a), to = tonumber(b), w = {}}
  for ad, val in string.gmatch(list, "(%x+)=(%x+)") do t.w[#t.w + 1] = {tonumber(ad, 16), tonumber(val, 16)} end
  holds[#holds + 1] = t
end
local peek = {}
for a in string.gmatch(os.getenv("PEEK") or "", "%x+") do peek[#peek + 1] = tonumber(a, 16) end
local function num(env, d) return tonumber(os.getenv(env) or d) end

local f = 0
local bank = -1
RUN_BANK = mem:install_write_tap(0x8000, 0xFFFF, "runbank", function(a, d) bank = d & 7 return d end)
local function sp(pc)
  if pc >= 0xC000 then return "f7" end
  if pc >= 0x8000 then return "b" .. tostring(bank) end
  if pc >= 0x4000 then return "f6" end
  return "ram"
end

-- MARIA register writes this frame
local mwr = {}
local mreg = {}
RUN_MARIA = mem:install_write_tap(0x20, 0x3F, "runmaria", function(a, d)
  mreg[a] = d & 0xFF
  mwr[#mwr + 1] = string.format("%02X=%02X", a, d & 0xFF)
  return d
end)

-- write taps
local wout
local wn, WMAX = 0, num("WMAX", "20000")
local WFROM, WTO = num("WFROM", "0"), num("WTO", "999999")
RUN_W = {}
for lo, hi in string.gmatch(os.getenv("WTAP") or "", "(%x+)%-(%x+)") do
  wout = wout or io.open("wtap.txt", "w")
  RUN_W[#RUN_W + 1] = mem:install_write_tap(tonumber(lo, 16), tonumber(hi, 16), "w" .. lo, function(a, d)
    if f >= WFROM and f <= WTO and wn < WMAX then
      wn = wn + 1
      local pc = cpu.state["PC"].value
      wout:write(string.format("%d %s %04X %04X %02X\n", f, sp(pc), pc, a, d & 0xFF))
    end
    return d
  end)
end
-- read taps
local rseen = {}
local RFROM, RTO = num("RFROM", "0"), num("RTO", "999999")
RUN_R = {}
for lo, hi in string.gmatch(os.getenv("RTAP") or "", "(%x+)%-(%x+)") do
  RUN_R[#RUN_R + 1] = mem:install_read_tap(tonumber(lo, 16), tonumber(hi, 16), "r" .. lo, function(a, d)
    if f >= RFROM and f <= RTO then
      local pc = cpu.state["PC"].value
      if pc ~= a then
        local k = sp(pc) .. string.format(":%04X", pc)
        local e = rseen[k]
        if not e then e = {lo = a, hi = a, n = 0, bank = bank, first = f} rseen[k] = e end
        if a < e.lo then e.lo = a end
        if a > e.hi then e.hi = a end
        e.n = e.n + 1
      end
    end
    return d
  end)
end
-- exec coverage
local xseen = {}
local XFROM, XTO = num("XFROM", "0"), num("XTO", "999999")
if os.getenv("EXEC") then
  RUN_X = mem:install_read_tap(0x4000, 0xFFFF, "runx", function(a, d)
    if f >= XFROM and f <= XTO and cpu.state["PC"].value == a then
      local k = sp(a) .. string.format(":%04X", a)
      if not xseen[k] then xseen[k] = f end
    end
    return d
  end)
end

local fout = io.open("frames.txt", "w")
local last = ""
local function dump()
  local o = io.open(string.format("dump_f%05d.bin", f), "wb")
  local t = {}
  for a = 0, 0xFFFF do
    local v = 0
    if a >= 0x40 and not (a >= 0x280 and a < 0x300) then v = mem:read_u8(a) end
    t[#t + 1] = string.char(v)
    if #t == 4096 then o:write(table.concat(t)) t = {} end
  end
  o:write(table.concat(t))
  o:close()
  local r = io.open(string.format("maria_f%05d.txt", f), "w")
  r:write("bank " .. tostring(bank) .. "\n" .. table.concat(mwr, " ") .. "\n")
  r:write(string.format("DPP %02X%02X CHARBASE %02X CTRL %02X\n", mreg[0x2C] or 0, mreg[0x30] or 0, mreg[0x34] or 0, mreg[0x3C] or 0))
  r:close()
end
local function finish()
  if fout then fout:close() fout = nil end
  if wout then wout:close() wout = nil end
  if next(rseen) then
    local keys = {}
    for k in pairs(rseen) do keys[#keys + 1] = k end
    table.sort(keys)
    local o = io.open("rtap.txt", "w")
    for _, k in ipairs(keys) do
      local e = rseen[k]
      o:write(string.format("%s reads %04X-%04X n=%d bank=%d first=%d\n", k, e.lo, e.hi, e.n, e.bank, e.first))
    end
    o:close()
    rseen = {}
  end
  if next(xseen) then
    local keys = {}
    for k in pairs(xseen) do keys[#keys + 1] = k end
    table.sort(keys)
    local o = io.open("exec.txt", "w")
    for _, k in ipairs(keys) do o:write(k .. " " .. tostring(xseen[k]) .. "\n") end
    o:close()
    xseen = {}
  end
end
RUN_F = emu.register_frame_done(function()
  f = f + 1
  local t, cur = f, nil
  for _, s in ipairs(steps) do
    if t <= s[1] then cur = s break end
    t = t - s[1]
  end
  for k, fl in pairs(stick) do fl:set_value((cur and cur[2]:find(k)) and 1 or 0) end
  fire:set_value((cur and cur[3] % 2 == 1) and 1 or 0)
  if fire2 then fire2:set_value((cur and math.floor(cur[3] / 2) % 2 == 1) and 1 or 0) end
  if pause then pause:set_value((cur and cur[3] % 8 >= 4) and 1 or 0) end
  if select then select:set_value((cur and cur[3] % 16 >= 8) and 1 or 0) end
  if reset then reset:set_value((cur and cur[3] >= 16) and 1 or 0) end
  if snaps[f] then M.video:snapshot() end
  if dumps[f] then dump() end
  mwr = {}
  if #peek > 0 then
    local v = {}
    for _, a in ipairs(peek) do v[#v + 1] = string.format("%02X", mem:read_u8(a)) end
    local s = table.concat(v, " ")
    if s ~= last then fout:write(string.format("%d %s\n", f, s)) last = s end
  end
  local p = pokes[f]
  if p then for _, w in ipairs(p) do mem:write_u8(w[1], w[2]) end end
  for _, h in ipairs(holds) do
    if f >= h.from and f <= h.to then for _, w in ipairs(h.w) do mem:write_u8(w[1], w[2]) end end
  end
  if f >= END then
    finish()
    M:exit()
  end
end)
RUN_STOP = emu.add_machine_stop_notifier(function() finish() end)
