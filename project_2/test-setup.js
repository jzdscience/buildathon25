// Load environment variables first
require('dotenv').config();

const { transcribeAudioFallback } = require('./src/services/speechToText');
const { generateSlides } = require('./src/services/slideGenerator');
const { createPresentation } = require('./src/services/presentationBuilder');

async function testApplication() {
  try {
    console.log('🎤 Testing Voice-to-Slide Generator...\n');
    
    // Test 1: Generate slides from sample transcript
    console.log('1. Testing slide generation...');
    const sampleTranscript = `
    Welcome everyone to today's presentation about the future of artificial intelligence in business.
    
    First, I want to discuss how AI is transforming customer service. Companies are now using chatbots and automated response systems to handle customer inquiries 24/7. This has improved response times significantly and reduced operational costs.
    
    Second, let's talk about data analysis and decision making. AI algorithms can process vast amounts of data much faster than humans, identifying patterns and trends that help businesses make better strategic decisions.
    
    Third, AI is revolutionizing operational efficiency. From supply chain optimization to predictive maintenance, machine learning is helping companies reduce waste and improve productivity across all departments.
    
    Finally, let's consider the future outlook. As AI technology continues to advance, we'll see even more innovative applications in areas like personalized marketing, automated workflows, and intelligent resource allocation.
    
    In conclusion, AI adoption is not just a trend but a necessity for businesses that want to remain competitive in the digital age. Thank you for your attention.
    `;
    
    const slideData = await generateSlides(sampleTranscript);
    console.log(`✅ Generated ${slideData.slides.length} slides`);
    console.log(`📋 Title: "${slideData.title}"`);
    
    // Test 2: Create HTML presentation
    console.log('\n2. Testing HTML presentation generation...');
    const sessionId = 'test-' + Date.now();
    const htmlPath = await createPresentation(slideData, sessionId);
    console.log(`✅ HTML presentation created: ${htmlPath}`);
    
    // Test 3: Display slide structure
    console.log('\n3. Generated slide structure:');
    slideData.slides.forEach((slide, index) => {
      console.log(`\n   Slide ${slide.slideNumber}: ${slide.title}`);
      slide.content.forEach(point => {
        console.log(`   • ${point.substring(0, 60)}${point.length > 60 ? '...' : ''}`);
      });
    });
    
    console.log('\n🎉 Test completed successfully!');
    console.log('\n📋 Next steps:');
    console.log('1. Set up your OpenAI API key in .env file');
    console.log('2. Run "npm start" to launch the application');
    console.log('3. Open http://localhost:3000 in your browser');
    console.log('4. Upload or record audio to generate presentations');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.log('\n🔧 Troubleshooting tips:');
    console.log('- Ensure all dependencies are installed: npm install');
    console.log('- For full functionality, set up OpenAI API key in .env');
    console.log('- Check that all required files are in place');
  }
}

// Run the test
if (require.main === module) {
  testApplication();
}

module.exports = { testApplication };