AC_PREREQ(2.52)

AC_INIT([Apertium English-Central Bikol], [0.1.0], [https://github.com/apertium/apertium-eng-bcl/issues], [apertium-eng-bcl], [https://wiki.apertium.org/wiki/Apertium-eng-bcl])
AM_INIT_AUTOMAKE
AC_PROG_AWK

PKG_CHECK_MODULES(APERTIUM, apertium >= 3.8.1)
PKG_CHECK_MODULES(LTTOOLBOX, lttoolbox >= 3.6.9)



PKG_CHECK_MODULES(CG3, cg3 >= 1.3.6)
PKG_CHECK_MODULES(APERTIUM_LEX_TOOLS, apertium-lex-tools >= 0.4.0)




AC_ARG_ENABLE([linter], AC_HELP_STRING([--enable-linter], [Lint files when compiling]))
AM_CONDITIONAL([ENABLE_LINTER], [test "x$enable_linter" = "xyes"])

AC_PATH_PROGS(ZCAT, [gzcat zcat], [false])
AS_IF([test x$ZCAT = xfalse], [AC_MSG_ERROR([You don't have zcat nor gzcat installed])])

m4_ifdef([AP_CHECK_LING],[],[AC_MSG_ERROR([AP_CHECK_LING not defined, is apertium.m4 in ACLOCAL_PATH? See: https://wiki.apertium.org/wiki/Installation_troubleshooting])])


AP_CHECK_LING([1], [apertium-eng])

AP_CHECK_LING([2], [apertium-bcl])

PKG_CHECK_MODULES(REGTEST, apertium-regtest >= 0.9.1, [],
                  [AC_MSG_WARN([Running tests requires apertium-regtest])])

AP_MKINCLUDE

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
