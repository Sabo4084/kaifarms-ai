import { useState } from 'react';

export default function Home(){
  const [question,setQuestion]=useState('');
  const [answer,setAnswer]=useState('');
  const [loading,setLoading]=useState(false);
  async function ask(){
    if(!question.trim()) return;
    setLoading(true); setAnswer('');
    try{
      const base=process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const r=await fetch(base+'/api/ai/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question})});
      const data=await r.json(); setAnswer(data.answer || 'No response received.');
    }catch(e){setAnswer('The API is not reachable. Start the backend and try again.');}
    finally{setLoading(false);}
  }
  return <main><section className="hero"><div className="badge">KAIFARMS AI</div><h1>Smarter Farming.<br/>Better Harvests.</h1><p>Your practical AI agricultural assistant for crops, livestock and farm records.</p><div className="grid"><div className="card"><h2>Ask KAIFARMS AI</h2><textarea value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Example: My maize leaves are turning yellow. What should I check?"/><button onClick={ask} disabled={loading}>{loading?'Thinking...':'Ask AI'}</button>{answer&&<div className="answer"><strong>Guidance</strong><p>{answer}</p></div>}</div><div className="card"><h2>Farm workspace</h2><p>Record activities, monitor your farm and build a useful history for better decisions.</p><ul><li>Farmer profile</li><li>Crop & livestock records</li><li>Expert escalation</li><li>Localized knowledge base</li></ul></div></div></section></main>
}
