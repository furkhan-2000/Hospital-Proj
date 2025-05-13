#!/bin/bash
mkdir -p app/static/assets/images app/static/assets/videos

# Hero
curl -o app/static/assets/images/doctor.jpg https://cdn.pixabay.com/photo/2014/12/10/21/01/doctor-563429_1280.jpg
curl -o app/static/assets/videos/hero.mp4 https://cdn.pixabay.com/video/2022/10/07/133898-758336558_large.mp4

# Compassion Slider
curl -o app/static/assets/images/emergency.jpg https://images.pexels.com/photos/236380/pexels-photo-236380.jpeg
curl -o app/static/assets/images/inpatient.jpg https://images.pexels.com/photos/263402/pexels-photo-263402.jpeg
curl -o app/static/assets/images/outpatient.jpg https://images.pexels.com/photos/4386467/pexels-photo-4386467.jpeg
curl -o app/static/assets/images/diagnostic.jpg https://images.pexels.com/photos/305568/pexels-photo-305568.jpeg
curl -o app/static/assets/images/surgical.jpg https://images.pexels.com/photos/7659573/pexels-photo-7659573.jpeg
curl -o app/static/assets/images/specialized.jpg https://images.pexels.com/photos/439227/pexels-photo-439227.jpeg
curl -o app/static/assets/images/administrative.jpg https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg

# Specialists
curl -o app/static/assets/images/specialist1.jpg https://www.img2link.com/images/2025/05/12/0ba6729c25207d75a9e3793cb8cb7c1f.jpg
curl -o app/static/assets/images/specialist2.jpg https://www.img2link.com/images/2025/05/12/252ac2d3310eb9e30d851045cf75b2ec.jpg
curl -o app/static/assets/images/specialist3.jpg https://www.img2link.com/images/2025/05/12/eada5219e288d5d860c3edea55903b61.jpg
curl -o app/static/assets/images/specialist4.jpg https://www.img2link.com/images/2025/05/12/f5182d714a51788c380e2f870f0e9442.jpg
curl -o app/static/assets/images/specialist5.jpg https://www.img2link.com/images/2025/05/12/6bb1058cd477b7e13bef4e6f9fbed4fb.jpg

# Visual Tour
curl -o app/static/assets/images/tour1.jpg https://www.img2link.com/images/2025/05/12/7cfe7ba67538acf0c55abe99584aae67.jpg
curl -o app/static/assets/images/tour2.jpg https://www.img2link.com/images/2025/05/12/c25140202319c1c028210b7fcbabeaa0.jpg
curl -o app/static/assets/images/tour3.jpg https://www.img2link.com/images/2025/05/12/aec773bc92639dc8560fd7ad01b44268.jpg
curl -o app/static/assets/images/tour4.jpg https://www.img2link.com/images/2025/05/12/bdce68d559786ecc740c0628f63c5b33.jpg
curl -o app/static/assets/images/tour5.jpg https://www.img2link.com/images/2025/05/12/25db0482dbc3dcf662c3d86ae94d07ee.jpg
curl -o app/static/assets/images/tour6.jpg https://www.img2link.com/images/2025/05/12/2feadc62f0a829a01534672f6318101a.jpg
curl -o app/static/assets/images/tour7.jpg https://assets.grok.com/anon-users/4c659a27-a758-4168-aaea-21fdc2047350/generated/HrQBcHEfdT0i2mEu/image.jpg

# Report Analyzer
curl -o app/static/assets/images/urinsights.jpg https://img.freepik.com/free-photo/lab-doctor-performing-medical-exam-urine_23-2149372021.jpg
curl -o app/static/assets/images/bloodinsights.jpg https://img.freepik.com/free-photo/coronavirus-blood-samples-arrangement-lab_23-2149107259.jpg

# Footer
curl -o app/static/assets/images/new_logo.png https://www.img2link.com/images/2025/05/11/75f87338d4ea408c849434f3150c7fd8.png

# Email Assets (placeholders; replace with your own if available)
# For logo-white.png, logo-icon.png, social-*.png, use placeholder images or create them
curl -o app/static/assets/images/logo-white.png https://via.placeholder.com/150x50/FFFFFF/000000?text=Logo
curl -o app/static/assets/images/logo-icon.png https://via.placeholder.com/28x28/FFFFFF/000000?text=Icon
curl -o app/static/assets/images/social-facebook.png "https://cdn-icons-png.freepik.com/256/1409/1409946.png?ga=GA1.1.750490589.1747143748&semt=ais_hybrid"
curl -o app/static/assets/images/social-linkedin.png "https://www.img2link.com/images/2025/05/13/067147b2aeb3f1af21948b2f486b2fbc.png"
curl -o app/static/assets/images/social-twitter.png "https://www.img2link.com/images/2025/05/13/0c86b4750c65a560e1684aa369dc6b44.png"

# Set permissions
chmod -R 755 app/static/assets
