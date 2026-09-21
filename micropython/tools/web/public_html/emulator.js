// int-hex conversion

// x = int
// return hex string
function int2hex(x) {
  return x.toString(16).toUpperCase();
}

// x = hex string
// return int
function hex2int(x) {
  return parseInt(x,16);
}

// hex string to synscan hex string
// LSB byte first, leading zeros
// x = hex string of length 2,4,6
// n = number of bytes 1,2,3
// return synscan hex string
function hex2shex(x,n) {
  r="";
  xp=("000000"+x).slice(-6) // 0-padding
  for(i=0;i<n;i++)
    r+=xp.slice(4-2*i,6-2*i);
  return r;
}

// n = number of bytes 1,2,3
// return synscan hex string
function int2shex(x,n) {
  return hex2shex(int2hex(x),n);
}

// x = synscan hex string of length 2,4,6
// return int
function shex2int(x) {
  l=x.length;
  r=0;
  for(i=l>>1<<1;i>=0;i-=2)
    r=(r<<8)+parseInt(x.slice(i,i+2),16);
  return r;
}

// dummy emulator
// supports command syntax
// not real emulator

// counts per full circle for each axis
const emu_axis_count = {
1:(0x0D331A*(179+13/60)/180+0.5)>>0,
2:(0x0D331A*(176+1/60)/180+0.5)>>0,
}
function femu_a(x) {
  axis=parseInt(x.slice(2,3),16);
  if(axis in emu_axis_count)
    return "="+int2shex(emu_axis_count[axis],3);
  return "!";
}

// firmware id
function femu_e(x) {
  return "="+int2shex(0xA11002,3);
}

// generic dummy confirm
function femu_dummy_confirm(x) {
  axis=parseInt(x.slice(2,3),16);
  if(axis>=1 && axis<=2)
    return "=";
  return "!";
}

// emulator function dictionary
const femu = {
  "a": femu_a, // counts per full circle
  "e": femu_e, // firmware version
  "I": femu_dummy_confirm, // manual slew speed
  "M": femu_dummy_confirm, // brake unused
  "T": femu_dummy_confirm, // goto slew speed
}

// just to make formatted response
// q = query string like ":e1"
// return answer string like "=021A0F"
function emulator(q) {
  if(q.slice(0,1) != ":")
    return "!";
  f=q.slice(1,2);
  if(f in femu)
    return femu[f](q);
  return "!";
}
