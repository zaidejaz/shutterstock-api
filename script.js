const images = require("./licensed_images_data_part_1.json");
const sstk = require("shutterstock-api");
const axios = require("axios");
const fs = require("fs");
const path = require("path");

sstk.setAccessToken(process.env.SHUTTERSTOCK_API_TOKEN);

const imagesApi = new sstk.ImagesApi();

const body = {
  "size": "huge"
};

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const downloadImage = async (url, tempFilepath, finalFilepath) => {
  const writer = fs.createWriteStream(tempFilepath);
  const response = await axios({
    url,
    method: 'GET',
    responseType: 'stream'
  });
  response.data.pipe(writer);
  return new Promise((resolve, reject) => {
    writer.on('finish', () => {
      fs.rename(tempFilepath, finalFilepath, (err) => {
        if (err) reject(err);
        else resolve();
      });
    });
    writer.on('error', (err) => {
      fs.unlink(tempFilepath, () => reject(err)); // Delete the temp file if an error occurs
    });
  });
};

const downloadImages = async () => {
  // Ensure the images folder exists
  const imagesFolder = path.join(__dirname, "images");
  if (!fs.existsSync(imagesFolder)) {
    fs.mkdirSync(imagesFolder);
  }

  for (let i = 0; i < images.length; i++) {
    const image = images[i];

    try {
      const data = await imagesApi.downloadImage(image.id, body);
      const imageUrl = data.url;
      const imageName = path.basename(imageUrl); // Extract filename from URL
      const finalFilepath = path.join(imagesFolder, imageName);
      const tempFilepath = path.join(imagesFolder, `${imageName}.part`);

      // Check if the image is already downloaded
      if (fs.existsSync(finalFilepath)) {
        console.log(`Image ${imageName} already downloaded.`);
        continue;
      }

      await downloadImage(imageUrl, tempFilepath, finalFilepath);
      console.log(`Downloaded image ${i + 1}: ${finalFilepath}`);
    } catch (error) {
      console.error(`Failed to download image ${image.id}:`, error);
    }

    // Delay of 12 seconds between each image
    if ((i + 1) % 5 !== 0) {
      await delay(12000);
    }

    // Delay of 36 seconds after every 100 images
    if ((i + 1) % 100 === 0) {
      await delay(36000);
    }
  }
};

downloadImages();
