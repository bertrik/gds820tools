#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>     // exit
#include <stdio.h>      // fopen etc
#include <string.h>     // strcmp


#define WIDTH           320
#define HEIGHT          256
#define HEIGHT_TRUNC    240
#define RAW_SIZE        40960

typedef struct {
    uint8_t r, g, b;
} rgb_t;

static void decode(const uint8_t in[], const rgb_t palette[16], uint8_t out[HEIGHT][WIDTH][3])
{
    int index = 0;
    int x;
    for (x = 0; x < WIDTH; x++) {
        int y;
        for (y = 0; y < HEIGHT; y += 2) {
            uint8_t b = in[index++];
            int n;
            // high nibble
            n = (b >> 4) & 0x0F;
            out[y][x][0] = palette[n].r;
            out[y][x][1] = palette[n].g;
            out[y][x][2] = palette[n].b;
            // low nibble
            n = (b >> 0) & 0x0F;
            out[y + 1][x][0] = palette[n].r;
            out[y + 1][x][1] = palette[n].g;
            out[y + 1][x][2] = palette[n].b;
        }
    }
}

static const rgb_t* create_palette(bool use_color)
{
    static const rgb_t color_palette[16] = {
        { 0x00, 0x00, 0x00},
        { 0x00, 0x00, 0x00},
        { 0xFF, 0xFF, 0x00},
        { 0x77, 0x77, 0x00},
        { 0x00, 0xFF, 0xFF},
        { 0x22, 0x44, 0x66},
        { 0x66, 0xFF, 0x66},
        { 0xFE, 0xFF, 0xFF},
        { 0x87, 0x88, 0x88},
        { 0x88, 0x22, 0x22},
        { 0x00, 0x00, 0x55},
        { 0xBB, 0xBB, 0xBB},
        { 0x99, 0x66, 0x33},
        { 0x88, 0x88, 0x88},
        { 0xFF, 0x22, 0x22},
        { 0xFF, 0xFF, 0xFF}
    };
    static const rgb_t grey_palette[16] = {
        { 0x88, 0x88, 0x88},
        { 0xFF, 0x00, 0x00},
        { 0x00, 0x00, 0x00},
        { 0xBB, 0x00, 0x00},
        { 0x00, 0x00, 0x00},
        { 0xBB, 0x00, 0x00},
        { 0x00, 0x00, 0x00},
        { 0x00, 0x00, 0x00},
        { 0x88, 0x00, 0x00},
        { 0xBB, 0x00, 0x00},
        { 0xFF, 0x00, 0x00},
        { 0x88, 0x00, 0x00},    //?
        { 0xBB, 0x00, 0x00},    //?
        { 0xFF, 0x00, 0x00},
        { 0x00, 0x00, 0x00},
        { 0xFF, 0x00, 0x00}
    };

    return use_color ? color_palette : grey_palette;
}

static bool read_raw(const char *filename, uint8_t buffer[RAW_SIZE])
{
    // open
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        perror("Could not open file for reading");
        return false;
    }
    
    // read
    if (fread(buffer, RAW_SIZE, 1, file) != 1) {
        perror("Could not read all input data");
        fclose(file);
        return false;
    }
    
    // close
    fclose(file);
    
    return true;
}

static bool write_pnm(uint8_t data[][320][3], int width, int height, const char *filename)
{
    // open file
    FILE *file = fopen(filename, "wb");
    if (file == NULL) {
        perror("Could not open file for writing");
        return false;
    }
    
    // write data
    fprintf(file, "P6 %d %d 255\n", width, height);
    if (fwrite(data, width * height * 3, 1, file) != 1) {
        perror("Could not write output data");
        fclose(file);
        return false;
    }
    
    // close
    fclose(file);

    return true;
}

static void usage(void)
{
    printf("Decodes an image data taken from the USB port of a GS820 oscilloscope to a PNM file.\n");
    printf("Usage:\n");
    printf("  decode <input-file> [color]\n");
}

// argv[1] : file name of the input file (output file will have .pnm appended)
// argv[2] : 1 = color, other = grey (optional, defaults to color)
int main(int argc, char *argv[])
{
    // parse args
    if (argc < 2) {
        usage();
        exit(-1);
    }
    const char* filename = argv[1];
    bool use_color = true;
    if (argc > 2) {
        use_color = (strcmp(argv[2], "color") == 0);
    }    
    
    // create palette
    const rgb_t *palette = create_palette(use_color);
    
    // read
    uint8_t inbuf[RAW_SIZE];
    if (!read_raw(filename, inbuf)) {
        exit(-1);
    }
    
    // decode
    uint8_t outbuf[HEIGHT][WIDTH][3];
    decode(inbuf, palette, outbuf);
    
    // write
    char outname[256];
    strcpy(outname, filename);
    strcat(outname, ".pnm");
    write_pnm(outbuf, WIDTH, HEIGHT_TRUNC, outname);

    return 0;
}

