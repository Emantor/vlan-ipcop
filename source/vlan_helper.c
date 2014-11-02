#include <stdio.h>

int main(int argc, char *argv[])
{

   if (!(initsetuid()) )
      exit(1);

   system("/etc/rc.d/rc.vlan");

   return 0;
}

