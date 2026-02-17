class Builtins:
    map_types_bss = {"int": "resd", "str":"resb", "byte":"resb","long":"resq"}
    map_max_values = {
        255: "byte",  # 2^8 - 1
        65535: "word",  # 2^16 - 1 (Useful if you add 16-bit support)
        4294967295: "int",  # 2^32 - 1
        18446744073709551615: "long"  # 2^64 - 1
    }
    @staticmethod
    def get_smallest_type(value):
        # Sort keys to check smallest limits first
        for limit in sorted(Builtins.map_max_values.keys()):
            if value <= limit:
                return Builtins.map_max_values[limit]
        return "long"

    map_type_sizes = {
        "int": 4,
        "str": 1,  # strings are per-byte, size depends on length
        "byte": 1,
        "word":2,
        "long": 8,
    }

    map_types_data = {"int": "dd", "str":"db", "byte":"db","long":"dq"}
    map_types_init = {"int":"dword", "byte":"byte","str":"byte", "long":"qword","word":"word"}
    code = {"puts_pm":"""
        puts_pm:
		
	        pusha
	   
	        mov edi, 0xb8000 ; video memory
	        
	   
	       ; mov ah, 0x07
	        ;mov ah,byte[esi+1] ; default attribute
	   
	    .puts_loop:
	        lodsb ; load byte from [esi] into al
	        or al, al
	        jz .done
	   
	        ; write char + attr to video memory
	        mov [edi], al
	       ;color
	        mov byte [edi+1], 0x0B
	   
	        ; mirror char + attr to console_buf
	        ;mov [edx], al
	        ;mov byte [edx+1], 0
	   
	        add edi, 2
	        ;add edx, 2
	        
	        
	  		jmp .puts_loop
	        ; wrap check (stop if >4000)
	        
	        	
	   
	    .done:
	        popa
	        ""","print":"""
		
	        pusha
	   
	        mov edi, dword [vga] ; video memory
	        
	   
	       ; mov ah, 0x07
	        ;mov ah,byte[esi+1] ; default attribute
	   
	    .puts_loop:
	        lodsb ; load byte from [esi] into al
	        or al, al
	        jz .done
	   
	        ; write char + attr to video memory
	        mov [edi], al
	       ;color
	        ;mov byte [edi+1], 0x0B
	   
	        ; mirror char + attr to console_buf
	        ;mov [edx], al
	        ;mov byte [edx+1], 0
	   
	        add edi, 2
	        add dword [vga],2
	        ;add edx, 2
	        
	        
	  		jmp .puts_loop
	        ; wrap check (stop if >4000)
	        
	        	
	   
	    .done:
	        popa
	        
	ret
""",
"int_to_str":"""; --- ASSUMPTIONS ---
        ; 1. The input number is at [EBP + 8]
        ; 2. The buffer address is at [EBP + 12]
        ; 3. We use EAX for the number, EBX for the divisor (10), and EDI for the buffer pointer.:
    push ebp
    mov ebp, esp
    pusha                   ; Save all general registers

    ; --- Setup ---
    mov eax, [ebp + 12]      ; EAX = The number to convert (e.g., 123)
    mov edi, [ebp + 8]     ; EDI = Address of the output buffer
    mov ebx, 10             ; EBX = Divisor (10)
    mov ecx, 0              ; ECX will count the number of digits pushed (Crucial fix!)
    
    ; Special case: If input is 0, we must push '0' once.
    cmp eax, 0
    jnz .non_zero_input
    
    ; Handle the input 0 case:
    mov al, '0'
    mov byte [edi], al      ; Write '0' to the buffer
    inc edi                 ; Move pointer
    jmp .done_string_output ; Skip loops

.non_zero_input:
    
    ; --- Step 1: Repeated Division Loop ---
.divide_loop:
    mov edx, 0              ; Clear EDX for IDIV
    idiv ebx                ; EDX = remainder (digit), EAX = quotient

    push edx                ; Push the remainder (the digit) onto the stack
    inc ecx                 ; INCREMENT DIGIT COUNTER (ECX)

    cmp eax, 0              ; Check if the quotient is 0
    jnz .divide_loop        
    
    ; --- Step 2: Convert Digits and Write to Buffer (Reverse Order) ---
    ; Loop runs ECX times (number of digits).
.store_loop:
    pop edx                 ; Pop the digit from the stack into EDX
                            ; (The digit is in the low byte, DL)

    add dl, '0'             ; Convert number to ASCII character
    mov [edi], dl           ; Write the ASCII character to the output buffer
    inc edi                 ; Move buffer pointer

    loop .store_loop        ; Use the LOOP instruction to decrement ECX and jump if not zero
                            ; (Note: LOOP uses ECX implicitly)

.done_string_output:
    ; --- Step 3: Null Termination ---
    mov byte [edi], 0       ; Terminate the string in the buffer
    
    ; --- Cleanup ---
    ; The stack is clean because we POPped exactly what we PUSHed (ECX times).
    popa                    
    pop ebp
    ret 8""", "str_to_int":"""; --- ASSUMPTIONS ---
; 1. The address of the string is at [EBP + 8]
; 2. Returns the result in EAX.

str_to_int:
    push ebp
    mov ebp, esp
    push ebx                ; Save EBX (will be used for the multiplier)
    push esi                ; Save ESI (will be used to walk the string)

    ; --- Setup ---
    mov esi, [ebp + 8]      ; ESI = Address of the string (e.g., "123\0")
    mov eax, 0              ; EAX = Accumulator (Final Integer Result), initialized to 0
    mov ebx, 10             ; EBX = Multiplier (10)

; --- Main Loop: Read Digits and Accumulate ---
.str_loop:
    mov al, byte [esi]      ; AL = Load current character from string
    inc esi                 ; Advance string pointer (ESI)
    
    cmp al, 0               ; Check for null terminator
    je .done                ; If AL is 0, exit the loop

    ; 1. Convert Character to Number (Digit = AL - '0')
    sub al, '0'             ; AL now holds the numerical digit (e.g., '3' -> 3)
    
    ; --- Check for Non-Digit Characters ---
    ; You might add checks here (cmp al, 0; cmp al, 9) to ensure AL is 0-9.
    
    ; 2. Accumulate: Result = (Result * 10) + New_Digit
    
    ; Multiply the current result (EAX) by 10
    ; We use the two-operand IMUL form (IMUL register, source) which keeps the result in the register.
    imul eax, ebx           ; EAX = EAX * 10 (Multiplies the running total by 10)
    
    ; Add the new digit (Note: EAX is 32-bit, so we zero-extend AL to EAX)
    movzx edx, al           ; EDX = The new 8-bit digit (zero-extended to 32-bit)
    add eax, edx            ; EAX = EAX + New_Digit
    
    jmp .str_loop           ; Loop back to process the next character

.done:
    ; EAX holds the final converted integer.
    
    ; --- Cleanup ---
    pop esi                 ; Restore saved registers
    pop ebx
    pop ebp
    ret 4                   ; Clean up the 1 argument (4 bytes) pushed by the caller""",
            "input":"""
.wait:
    in al, 0x64            ; status port
    test al, 1             ; output buffer full?
    jz .wait
    in al, 0x60            ; scan code
    test al, 0x80          ; ignore break codes
    jnz .wait

    ; ---- Modifier keys ----
    cmp al, 0x1D           ; Ctrl pressed
    je .ctrl_press
    cmp al, 0x9D           ; Ctrl released
    je .ctrl_release

    ; ---- Letters A–Z ----
    cmp al, 0x1E           ; A
    je .key_A
    cmp al, 0x30           ; B
    je .key_B
    cmp al, 0x2E           ; C
    je .key_C
    cmp al, 0x20           ; D
    je .key_D
    cmp al, 0x12           ; E
    je .key_E
    cmp al, 0x21           ; F
    je .key_F
    cmp al, 0x22           ; G
    je .key_G
    cmp al, 0x23           ; H
    je .key_H
    cmp al, 0x17           ; I
    je .key_I
    cmp al, 0x24           ; J
    je .key_J
    cmp al, 0x25           ; K
    je .key_K
    cmp al, 0x26           ; L
    je .key_L
    cmp al, 0x32           ; M
    je .key_M
    cmp al, 0x31           ; N
    je .key_N
    cmp al, 0x18           ; O
    je .key_O
    cmp al, 0x19           ; P
    je .key_P
    cmp al, 0x10           ; Q
    je .key_Q
    cmp al, 0x13           ; R
    je .key_R
    cmp al, 0x1F           ; S
    je .key_S
    cmp al, 0x14           ; T
    je .key_T
    cmp al, 0x16           ; U
    je .key_U
    cmp al, 0x2F           ; V
    je .key_V
    cmp al, 0x11           ; W
    je .key_W
    cmp al, 0x2D           ; X
    je .key_X
    cmp al, 0x15           ; Y
    je .key_Y
    cmp al, 0x2C           ; Z
    je .key_Z

    ; ---- Other Example Keys ----
    cmp al, 0x1C           ; Enter
    je .key_enter

    ; Nothing matched
    ret

; ------------------------------
; Modifier handlers
; ------------------------------
.ctrl_press:
    ;mov byte [ctrl_down], 1
    ret

.ctrl_release:
    ;mov byte [ctrl_down], 0
    ret

.r_key:
    ;cmp byte [ctrl_down], 1
    ;jne .not_ctrl_r
    mov al, 0xFE
    out 0x64, al
    ret
.not_ctrl_r:
    ret

; ------------------------------
; Letter return handlers
; ------------------------------
.key_A: mov al, 'A'  ; scancode 0x1E
        ret
.key_B: mov al, 'B'
        ret
.key_C: mov al, 'C'
        ret
.key_D: mov al, 'D'
        ret
.key_E: mov al, 'E'
        ret
.key_F: mov al, 'F'
        ret
.key_G: mov al, 'G'
        ret
.key_H: mov al, 'H'
        ret
.key_I: mov al, 'I'
        ret
.key_J: mov al, 'J'
        ret
.key_K: mov al, 'K'
        ret
.key_L: mov al, 'L'
        ret
.key_M: mov al, 'M'
        ret
.key_N: mov al, 'N'
        ret
.key_O: mov al, 'O'
        ret
.key_P: mov al, 'P'
        ret
.key_Q: mov al, 'Q'
        ret
.key_R: mov al, 'R'
        ret
.key_S: mov al, 'S'
        ret
.key_T: mov al, 'T'
        ret
.key_U: mov al, 'U'
        ret
.key_V: mov al, 'V'
        ret
.key_W: mov al, 'W'
        ret
.key_X: mov al, 'X'
        ret
.key_Y: mov al, 'Y'
        ret
.key_Z: mov al, 'Z'
        ret

.key_enter:
        mov al, 0x0D
        ret
""",
            "init_heap":
            """
    push ebp
    mov ebp, esp
    push eax ; Save registers
    push ebx
    
    ; 1. Set the HEAP_HEAD pointer
    mov ebx, heap       
    mov [HEAP_HEAD], ebx

    ; 2. Write the Status (FREE = 0)
    mov byte [ebx + HEADER_STATUS_OFFSET], 0  

    ; 3. Write the Size (9991 usable bytes)
    mov eax, 10000      
    sub eax, HEADER_TOTAL_SIZE 
    mov [ebx + HEADER_SIZE_OFFSET], eax       

    ; 4. Write the Next Pointer (NULL = 0)
    mov dword [ebx + HEADER_NEXT_OFFSET], 0   

    pop ebx
    pop eax
    pop ebp
    ret""",
    "alloc":"""
    push ebp
    mov ebp, esp
    push ebx                  
    push esi

    mov ebx, [ebp + 8]        ; EBX = Requested data size (R_size)
    mov esi, [heap_head]      ; ESI = Current block pointer

.find_block_loop:
    cmp esi, 0                
    je .fail_allocation       

    ; 1. Check Status 
    cmp byte [esi + HEADER_STATUS_OFFSET], 1
    je .move_to_next          
    
    ; 2. Check Size 
    mov eax, [esi + HEADER_SIZE_OFFSET]        ; EAX = Block's stored usable size
    cmp eax, ebx                               ; Compare Block Size (EAX) with Requested Size (EBX)
    jge .found_block                           ; If block is big enough, jump to success

.move_to_next:
    mov esi, [esi + HEADER_NEXT_OFFSET]        ; ESI = Load the address of the next block
    jmp .find_block_loop

.found_block:
    ; --- 1. Calculate and Check Remainder for Splitting ---
    mov ecx, eax              ; ECX = Block's original Usable Size
    sub ecx, ebx              ; ECX = Remainder Usable Size
    
    cmp ecx, MIN_SPLIT_SIZE   ; Check if Remainder >= 13 bytes
    jl .no_split_needed       
    
    ; --- BLOCK SPLIT LOGIC ---
    mov edx, esi              
    add edx, HEADER_TOTAL_SIZE ; EDX = Start address of USABLE data area
    add edx, ebx              ; EDX = Start address of the NEW metadata block
    
    ; Write the HEADER for the NEW free block
    mov byte [edx + HEADER_STATUS_OFFSET], 0  ; Status: FREE (0)
    sub ecx, HEADER_TOTAL_SIZE               ; ECX = Final Usable Size for new block
    mov [edx + HEADER_SIZE_OFFSET], ecx      
    mov eax, [esi + HEADER_NEXT_OFFSET]      ; Get old NEXT pointer
    mov [edx + HEADER_NEXT_OFFSET], eax      ; Set new block's NEXT pointer
    
    ; Update the OLD block's fields
    mov [esi + HEADER_NEXT_OFFSET], edx      ; Old block now points to the new remainder block
    mov [esi + HEADER_SIZE_OFFSET], ebx      ; Update old block size to R_size (e.g., 8)
    
    jmp .block_finalized_used

.no_split_needed:
    ; No changes to size/next needed.
        
.block_finalized_used:
    ; 2. Mark the block as USED
    mov byte [esi + HEADER_STATUS_OFFSET], 1  

    ; 3. Return the usable data address
    mov eax, esi
    add eax, HEADER_TOTAL_SIZE                ; EAX = USABLE address

    jmp .return_success

.fail_allocation:
    mov eax, 0                                ; Return NULL (0)

.return_success:
    pop esi               
    pop ebx
    pop ebp
    ret 4""",
    "color_screen":"""
    push ebp
    mov ebp,esp
    mov edi, 0xB8000
    mov ah, byte [ebp+8]        ; background
    shl ah, 4        ; move into bits 6–4
    or  ah, byte [ebp+12]        ; foreground
    mov al, ' '      ; space character
    ;mov ax, 0x1F20        ; ' ' + color (blue bg, white fg)
    mov ecx, 80*25
    rep stosw
     mov esp,ebp
     pop ebp
     ret 8""",
    "delay":"""delay:
    push ebp
    mov ebp, esp
    push ecx            ; Save ECX since we will use it for the loop counter

    mov ecx, [ebp + 8]  ; ECX = N_COUNT (The delay value passed from your language)

.delay_loop:
    ; The loop body should be as small as possible to minimize cycle variance.
    ; NOP is a single-byte instruction that does nothing, but provides a target for the loop.
    nop 
    
    ; The DEC and JNE instructions are what actually take up the time.
    loop .delay_loop    ; Decrements ECX and jumps back if ECX is not zero (JNZ)

    pop ecx             ; Restore ECX
    pop ebp
    ret 4"""}



class Generate:
    #modified to start at a diff index
    @staticmethod
    def str_reassign_i(name, string,j):
        code = ""
        len_str = len(string) - 3

        state = 0
        for i, v in enumerate(string):
            if v == '"':
                if state == 1:
                    break
                state += 1
                continue
            code += f"\tmov byte [{name}+{i+j - 1}], '{v}'\n"
        code += f"mov byte [{name}+{len_str+j - 1}], 0 \n"
        return code
    @staticmethod
    def str_reassign(name,string):
        code=""
        len_str = len(string)-3

        state = 0
        for i, v in enumerate(string):
            if v == '"':
                if state == 1:
                    break
                state += 1
                continue
            code+=f"\tmov byte [{name}+{i - 1}], '{v}'\n"
        code+=f"mov byte [{name}+{len_str - 1}], 0 \n"
        return code



    # --- Function to rewrite the line ---
    @staticmethod
    def rewrite_double_dereference(match):
        TEMP_REG = "ebx"

        # match.group(1): The full instruction being rewritten (e.g., 'mov al, ')
        # match.group(2): The inner EBP address (e.g., 'ebp+12')

        # Instruction 1: Load the pointer from the stack into EBX
        # We load the full address (4 bytes)
        setup_instruction = f"mov {TEMP_REG}, [{match.group(3)}]"

        # Instruction 2: Rewrite the original instruction to use the register
        # We replace the entire [[...]] with just [ebx]
        final_instruction = f"{match.group(1)} [{TEMP_REG}]"

        # Return the new two-line assembly block, separated by a newline
        return f"{setup_instruction}\n{final_instruction}"
