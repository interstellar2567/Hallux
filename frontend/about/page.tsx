export default function AboutPage() {
  return (
    <div className="bg-[#030303] min-h-screen">
      <div className="container mx-auto px-4 py-24">
        <div className="text-center mb-16 relative max-w-3xl mx-auto">
          <div className="absolute inset-0.5 -translate-y-1/2 bg-gradient-to-br from-indigo-500/20 to-rose-500/20 blur-3xl rounded-full w-1/2 mx-auto" />
          <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 via-white to-rose-300">
            About Hallux
          </h1>
          <p className="text-lg text-white/60">
            Our mission is to make AI-generated content more reliable and trustworthy for everyone.
          </p>
        </div>

        <div className="max-w-4xl mx-auto space-y-12">
          {/* Our Mission */}
          <div className="p-8 rounded-2xl bg-white/[0.05] border border-white/10 backdrop-blur-xl">
            <h2 className="text-3xl font-bold text-white mb-4">Our Mission</h2>
            <p className="text-white/60 leading-relaxed">
              In the age of generative AI, Large Language Models (LLMs) can produce incredible content, but they also have a tendency to "hallucinate" facts and citations. This can spread misinformation and erode trust in AI systems. Hallux was created to combat this problem by providing a robust, multi-layered verification system that checks the authenticity of citations in real-time. We aim to be the standard for AI content verification.
            </p>
          </div>

          {/* The Problem */}
          <div className="p-8 rounded-2xl bg-white/[0.05] border border-white/10 backdrop-blur-xl">
            <h2 className="text-3xl font-bold text-white mb-4">The Problem We Solve</h2>
            <p className="text-white/60 leading-relaxed">
              AI-generated content is becoming ubiquitous, from academic research to news articles. While powerful, the risk of fabricated information is significant. A fake citation can undermine the credibility of an entire work. Manually verifying every source is time-consuming and often impractical. Hallux automates this process, providing instant feedback and ensuring the integrity of your content.
            </p>
          </div>

          {/* Our Vision */}
          <div className="p-8 rounded-2xl bg-white/[0.05] border border-white/10 backdrop-blur-xl">
            <h2 className="text-3xl font-bold text-white mb-4">Our Vision</h2>
            <p className="text-white/60 leading-relaxed">
              We envision a future where AI is a reliable partner in content creation. Our goal is to provide developers, writers, and researchers with the tools they need to confidently use AI. By making citation verification seamless and accessible, we hope to foster a more trustworthy digital ecosystem. This project was built for the ByteQuest Hackathon 2026 to showcase the potential of such a system.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
