# Makefile for ErrorBuddy
#   make              build the compiler
#   make run          compile examples/valid.txt
#   make run FILE=x   compile another file
#   make test         run every example and compare with the expected output
#   make web          start the web playground on http://localhost:8795
#   make clean        remove build files

CXX      = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -pedantic -O2
TARGET   = errorbuddy
OBJS     = main.o lexer.o parser.o
FILE    ?= examples/valid.txt

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $(OBJS)

%.o: %.cpp lexer.h parser.h
	$(CXX) $(CXXFLAGS) -c $<

run: $(TARGET)
	./$(TARGET) $(FILE)

test: $(TARGET)
	@pass=0; fail=0; \
	for f in examples/*.txt; do \
		expected=examples/expected/$$(basename $$f .txt).out; \
		if ./$(TARGET) $$f | diff -u $$expected - > /dev/null; then \
			echo "PASS  $$f"; pass=$$((pass + 1)); \
		else \
			echo "FAIL  $$f  (see: ./$(TARGET) $$f | diff $$expected -)"; fail=$$((fail + 1)); \
		fi; \
	done; \
	echo "$$pass passed, $$fail failed"; \
	[ $$fail -eq 0 ]

web: $(TARGET)
	python3 web/server.py

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all run test web clean
