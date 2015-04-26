// r0: Timeout counter
// r1: Advance bit coming from PRU1
// r2: Ptr to DRAM[0]

// r0: GP Ptr
// r1: GP Tmr
// r2: Reserved
// r3: Reserved
// r4: DAQ_State
// r5: DAQ_Config
// r6: DAQ_Config
// r7: DAQ_Config
// r8: DAQ_Config



/////////////////////////////////////////
// 		SETTINGS 	/////////
/////////////////////////////////////////
//#define TO_EN

/////////////////////////////////////////
// 		STRUCTS 	/////////
/////////////////////////////////////////
.struct General
	.u32	Ptr
	.u32	Tmr
	.u32	Cpr
	.u32	Extension
.ends	
.assign General, r0, r3, GP

// bit0: BUSY
// bit1: ON STBY
// bit2: Collecting Data
// bit3: Tmr Interrupt

//conversion control
#define COLL	2 // Collection active bit
#define CINT    3 // CONVST interrupt bit

// bits for sample control
#define TRGD	0 // Trigger'd bit
#define ARMD	1 //  Armed bit
.struct DAQ_State
	.u32	Sample_Abs
	.u32	Sample
	.u32	PRU0_Ptr
	.u32	PRU1_Ptr
	.u32	TapeHD_Offset
	.u8	PRU0_State
	.u8	PRU1_State
	.u8 	Super_Sample
	.u8 	Sub_Sample //0 or 1... as ADC always grabs two channels at a time. 
	.u8		Sample_Ctrl
.ends
.assign DAQ_State, r4, r10.b0, DQ


.struct DAQ_Config
	.u32	Samp_Len	// samples
	.u32	Samp_Rate	// loops
	.u32	Data_Dst	// address 
	.u32	TO		// TimeOut:loops
	.u32	Trg_Threshold
.ends
.assign DAQ_Config, r11, r15, DAQConf

.macro  NOP32
		NOP
		NOP
		NOP
.endm

/////////////////////////////////////////
// 		CONSTANTS 	/////////
/////////////////////////////////////////
// ADC Data Pins
#define DB0     16  // P9-26  //ONLY PRU1
#define DB1     1   // P8-46  //ONLY PRU1
#define DB2     0   // P8-45  //ONLY PRU1
#define DB3     3   // P8-44  //ONLY PRU1
#define DB4     2   // P8-43  //ONLY PRU1
#define DB5     5   // P8-42  //ONLY PRU1
#define DB6     4   // P8-41  //ONLY PRU1
#define DB7     7   // P8-40  //ONLY PRU1
#define DB8     6   // P8-39  //ONLY PRU1
#define DB9     9   // P8-29  //ONLY PRU1
#define DB10    10   // P8-28  //ONLY PRU1
#define DB11	8  // P8-27  //ONLY PRU1

// ADC Outputs
#define bCONVST	1	// P9-29
#define bWR		0	// P9-31
#define bRD		2	// P9-30


// ADC Inputs
#define BUSY	5//7	// P9-27 (datasheet say P9-27 = PRU1_R31_7)




//Volatile PRU mem space = (0x0000)
#define SHAREDh			0x0000
//HOST (Python) Memory space = (0x0000)_python, (0x0000)_PRU0, (0x2000)_PRU1
#define HOST_DDR_ADDRh	0x0004
#define HOST_SLh		0x0008	// sample length
#define HOST_SRh		0x000C
#define HOST_THRh		0x0010
//PRU Personal Space = (0x0000)_PRUx
#define PRU_STATEh		0x0014


/////////////////////////////////////////
// 		MACROS 	/////////
/////////////////////////////////////////

.macro	Sub_Sample_Controller 
.mparam LABEL
		QBEQ RELOAD, DQ.Sub_Sample, 1
          MOV DQ.Sub_Sample, 1 				//bit must be zero. setting it to 1 .
          QBA LABEL
		RELOAD:
		MOV DQ.Sub_Sample, 0 				//bit must be 1. Set it to 0
.endm