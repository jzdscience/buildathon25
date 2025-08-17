const OpenAI = require('openai');

// Initialize OpenAI client only if API key is available
let openai = null;
if (process.env.OPENAI_API_KEY) {
  openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
  });
}

async function generateSlides(transcript) {
  try {
    console.log('Generating slides from transcript...');
    
    // Use fallback if OpenAI is not available
    if (!openai) {
      console.log('OpenAI API not available, using fallback method');
      return generateSlidesFallback(transcript);
    }
    
    const prompt = `
You are an expert presentation designer. Convert the following spoken transcript into a professional slide deck with exactly 5-8 slides.

TRANSCRIPT:
"${transcript}"

Create a JSON response with the following structure:
{
  "title": "Main presentation title",
  "slides": [
    {
      "slideNumber": 1,
      "title": "Slide title",
      "content": ["Bullet point 1", "Bullet point 2", "Bullet point 3"],
      "speakerNotes": "Detailed speaker notes for this slide explaining what to say and any additional context"
    }
  ]
}

Requirements:
- Create 5-8 slides total (including title slide)
- First slide should be a title slide with the main topic
- Each content slide should have 2-4 bullet points
- Use clear, professional language
- Include comprehensive speaker notes (2-3 sentences minimum per slide)
- Structure the content logically with smooth flow between slides
- Make bullet points concise but informative
- Ensure the presentation tells a complete story
- Speaker notes should expand on the bullet points and provide additional context

Return only valid JSON, no additional text.`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'You are a professional presentation designer who creates engaging, well-structured slide decks. Always respond with valid JSON only.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 2000
    });

    const response = completion.choices[0].message.content.trim();
    
    // Clean up the response to ensure it's valid JSON
    let cleanedResponse = response;
    if (cleanedResponse.startsWith('```json')) {
      cleanedResponse = cleanedResponse.replace(/```json\n?/, '').replace(/\n?```$/, '');
    }
    
    const slideData = JSON.parse(cleanedResponse);
    
    // Validate the structure
    if (!slideData.title || !slideData.slides || !Array.isArray(slideData.slides)) {
      throw new Error('Invalid slide data structure received from AI');
    }
    
    // Ensure we have at least 5 slides
    if (slideData.slides.length < 5) {
      throw new Error('Generated presentation has fewer than 5 slides');
    }
    
    // Validate each slide
    slideData.slides.forEach((slide, index) => {
      if (!slide.title || !slide.content || !Array.isArray(slide.content)) {
        throw new Error(`Invalid slide structure at slide ${index + 1}`);
      }
      if (!slide.speakerNotes) {
        slide.speakerNotes = `Speaker notes for slide ${index + 1}: ${slide.title}`;
      }
      slide.slideNumber = index + 1;
    });
    
    console.log(`Generated ${slideData.slides.length} slides successfully`);
    return slideData;
    
  } catch (error) {
    console.error('Error generating slides:', error);
    
    if (error.message.includes('JSON') || 
        error.code === 'insufficient_quota' || 
        error.code === 'invalid_api_key' ||
        error.status === 429 ||
        error.status === 401) {
      // Fallback to a structured format for API issues
      console.log('API issue detected, using fallback slide generation');
      return generateSlidesFallback(transcript);
    }
    
    throw new Error('Failed to generate slides: ' + error.message);
  }
}

function generateSlidesFallback(transcript) {
  console.log('Using fallback slide generation method');
  
  // Simple keyword extraction and slide generation
  const words = transcript.toLowerCase().split(/\s+/);
  const sentences = transcript.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  // Extract key topics
  const keyTopics = extractKeyTopics(transcript);
  
  const slides = [];
  
  // Title slide
  slides.push({
    slideNumber: 1,
    title: keyTopics.title || "Presentation Overview",
    content: [
      "Key insights from audio presentation",
      "Main topics and discussions",
      "Important findings and conclusions"
    ],
    speakerNotes: "Welcome to this presentation. Today we'll be covering the main topics discussed in the audio recording, including key insights and important findings."
  });
  
  // Content slides
  const contentChunks = chunkContent(sentences, 4);
  contentChunks.forEach((chunk, index) => {
    const slideTitle = keyTopics.topics[index] || `Topic ${index + 1}`;
    const bulletPoints = chunk.map(sentence => 
      sentence.trim().substring(0, 80) + (sentence.length > 80 ? '...' : '')
    ).slice(0, 4);
    
    slides.push({
      slideNumber: index + 2,
      title: slideTitle,
      content: bulletPoints,
      speakerNotes: `This slide covers ${slideTitle.toLowerCase()}. Key points include: ${chunk.join(' ').substring(0, 200)}...`
    });
  });
  
  // Conclusion slide
  slides.push({
    slideNumber: slides.length + 1,
    title: "Conclusion",
    content: [
      "Summary of key points",
      "Main takeaways",
      "Next steps and considerations"
    ],
    speakerNotes: "In conclusion, we've covered the main topics from the presentation. The key takeaways include the points discussed throughout the slides."
  });
  
  return {
    title: keyTopics.title || "Audio Presentation Summary",
    slides: slides.slice(0, 8) // Ensure max 8 slides
  };
}

function extractKeyTopics(transcript) {
  const commonWords = new Set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them']);
  
  const words = transcript.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 3 && !commonWords.has(word));
  
  const wordFreq = {};
  words.forEach(word => {
    wordFreq[word] = (wordFreq[word] || 0) + 1;
  });
  
  const topWords = Object.entries(wordFreq)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 6)
    .map(([word]) => word);
  
  return {
    title: topWords.length > 0 ? 
      topWords.slice(0, 2).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' & ') + ' Overview' :
      'Presentation Overview',
    topics: [
      'Introduction',
      topWords[0] ? topWords[0].charAt(0).toUpperCase() + topWords[0].slice(1) : 'Main Topic',
      topWords[1] ? topWords[1].charAt(0).toUpperCase() + topWords[1].slice(1) : 'Key Concepts',
      'Analysis & Insights',
      'Implementation',
      'Conclusion'
    ]
  };
}

function chunkContent(sentences, maxChunks) {
  const chunkSize = Math.ceil(sentences.length / maxChunks);
  const chunks = [];
  
  for (let i = 0; i < sentences.length; i += chunkSize) {
    chunks.push(sentences.slice(i, i + chunkSize));
  }
  
  return chunks.slice(0, maxChunks);
}

module.exports = { generateSlides };