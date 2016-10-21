CC := gcc
LDFLAGS := $(shell python-config --libs)
INCLUDES := $(shell python-config --includes)

flashplayer: flashplayer.o
	$(CC) -o $@ $^ $(LDFLAGS)

flashplayer.o: flashplayer.c
	$(CC) -c $^ $(INCLUDES)

flashplayer.c: flashplayer.py
	@echo cython --embed flashplayer.py
	@cython --embed flashplayer.py

all: flashplayer

clean:
	@rm -vf *.o *.c flashplayer
