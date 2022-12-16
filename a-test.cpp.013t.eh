
;; Function main (main, funcdef_no=1731, decl_uid=44211, cgraph_uid=465, symbol_order=495)

int main ()
{
  int i;
  double f;
  int cnt;
  int D.49055;

  cnt = 0;
  i = 0;
  goto <D.44219>;
  <D.44218>:
  cnt = cnt + 1;
  if (cnt > 5) goto <D.49052>; else goto <D.49053>;
  <D.49052>:
  f = (double) cnt;
  goto <D.49054>;
  <D.49053>:
  _1 = (double) cnt;
  f = f - _1;
  <D.49054>:
  i = i + 1;
  <D.44219>:
  if (i <= 9) goto <D.44218>; else goto <D.44216>;
  <D.44216>:
  D.49055 = 0;
  goto <D.49056>;
  D.49055 = 0;
  goto <D.49056>;
  <D.49056>:
  return D.49055;
}



;; Function __static_initialization_and_destruction_0 (_Z41__static_initialization_and_destruction_0ii, funcdef_no=2226, decl_uid=49044, cgraph_uid=960, symbol_order=1017)

void __static_initialization_and_destruction_0 (int __initialize_p, int __priority)
{
  if (__initialize_p == 1) goto <D.49057>; else goto <D.49058>;
  <D.49057>:
  if (__priority == 65535) goto <D.49059>; else goto <D.49060>;
  <D.49059>:
  std::ios_base::Init::Init (&__ioinit);
  __cxxabiv1::__cxa_atexit (__dt_comp , &__ioinit, &__dso_handle);
  goto <D.49061>;
  <D.49060>:
  <D.49061>:
  goto <D.49062>;
  <D.49058>:
  <D.49062>:
  return;
}



;; Function _GLOBAL__sub_I_main (_GLOBAL__sub_I_main, funcdef_no=2227, decl_uid=49050, cgraph_uid=961, symbol_order=1136)

void _GLOBAL__sub_I_main ()
{
  __static_initialization_and_destruction_0 (1, 65535);
  return;
}


