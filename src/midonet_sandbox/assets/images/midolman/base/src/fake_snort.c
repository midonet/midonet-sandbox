#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>

#include <pcap/pcap.h>

static int debug = 0;

struct context_t {
  pcap_t* pcap;
  const char* pattern;
  int pattern_len;
};

// O(m*n), but I don't care. n is bounded at MTU, m is small
const char* find_pattern(const char* haystack, int haystack_len,
			 const char* needle, int needle_len) {
  int i,j;
  for (i = 0; i < haystack_len; i++) {
    for (j = 0; j < needle_len && i+j < haystack_len; j++) {
      if (haystack[i+j] != needle[j]) {
	break;
      }
    }
    if (j == needle_len) {
      return &haystack[i];
    }
  }
  return NULL;
}

void handler(u_char *user, const struct pcap_pkthdr *h,
	     const u_char *bytes) {
  struct context_t* context = (struct context_t*)user;

  int i, err;
  if (debug) {
    printf("Received %d bytes: ", h->caplen);
    for (i = 0; i < h->caplen; i++) {
      printf("%02x", bytes[i]);
    }
    printf("\n");
  }

  if (find_pattern(bytes, h->caplen,
		   context->pattern,
		   context->pattern_len) == NULL) {
    err = pcap_sendpacket(context->pcap, bytes, h->caplen);
    if (err != 0) {
      fprintf(stderr, "Couldn't bounce packet: %d, %s\n",
	      err, pcap_strerror(err));
    }
  }
}


int
capture_loop(const char* interface, const char* pattern, int pattern_len) {
  char errbuf[PCAP_ERRBUF_SIZE];
  int err;

  struct context_t context;
  context.pattern = pattern;
  context.pattern_len = pattern_len;

  context.pcap = pcap_create(interface, (char*)&errbuf);
  if (context.pcap == NULL) {
    fprintf(stderr, "Couldn't create pcap %s\n", errbuf);
    return 1;
  }

  err = pcap_set_promisc(context.pcap, 1);
  if (err != 0) {
    fprintf(stderr, "Couldn't set promisc mode: %d, %s\n",
	    err, pcap_strerror(err));
    return err;
  }

  err = pcap_set_timeout(context.pcap, 10); //ms
  if (err != 0) {
    fprintf(stderr, "Set timeout failed: %d, %s\n",
	    err, pcap_strerror(err));
      return err;
  }

  err = pcap_activate(context.pcap);
  if (err != 0) {
    fprintf(stderr, "Activation failed: %d, %s\n",
	    err, pcap_strerror(err));
      return err;
  }

  err = pcap_loop(context.pcap, -1, &handler, (u_char*)&context);
  if (err != 0) {
    fprintf(stderr, "Error looping: %d, %s\n", err, pcap_strerror(err));
    return err;
  }
  return 0;
}

char char2byte(char character) {
  if (character >= 'A' && character <= 'F') {
    return character - 'A' + 10;
  } else if (character >= 'a' && character <= 'f') {
    return character - 'a' + 10;
  } else if (character >= '0' && character <= '9') {
    return character - '0';
  } else {
    fprintf(stderr, "Invalid character in pattern %c\n", character);
    return -1;
  }
}

int
main(int argc, char* argv[]) {
  char* interface = NULL;
  char* pattern = NULL;

  int c;

  while (1) {
    static struct option long_options[] =
      {
	{"debug",     no_argument,       &debug, 1},
	{"interface", required_argument, 0, 'i'},
	{"block-pattern",   required_argument, 0, 'p'},
	{0, 0, 0, 0}
      };
    int option_index = 0;

    c = getopt_long (argc, argv, "i:p:",
		     long_options, &option_index);
    if (c == -1) {
      break;
    }

    switch (c) {
    case 'i':
      interface = strdup(optarg);
      break;
    case 'p':
      pattern = strdup(optarg);
      break;
    }
  }
  if (pattern == NULL || interface == NULL) {
    fprintf(stderr,
	    "Usage: %s --interface <iface> --block-pattern <hex-pattern>\n",
	    argv[0]);
    return 1;
  }

  if (strlen(pattern) % 2 == 1) {
    fprintf(stderr, "Pattern must have even number of characters\n");
    return 1;
  }

  int bytes_len = strlen(pattern)/2;
  int i = 0;
  char* pattern_bytes = (char*)malloc(bytes_len);

  for (i = 0; i < bytes_len*2; i += 2) {
    char first_nibble = char2byte(pattern[i]);
    char second_nibble = char2byte(pattern[i+1]);

    if (first_nibble < 0 || second_nibble < 0) {
      fprintf(stderr, "Cannot convert pattern\n");
      return 1;
    }
    pattern_bytes[i/2] = (first_nibble << 4) & 0xF0 | (second_nibble & 0x0F);
  }

  printf("Blocking pattern: ");
  for (c = 0; c < bytes_len; c++) {
    printf("%hhx ", pattern_bytes[c]);
  }
  printf("\n");

  return capture_loop(interface, pattern_bytes, bytes_len);
}
